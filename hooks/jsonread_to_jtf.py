#!/usr/bin/env python3
"""
PostToolUse-хук для Claude Code: при чтении .json подменяет вывод Read на компактный
JTF, чтобы сэкономить токены контекста. Структура данных сохраняется (round-trip
проверяется прямо в хуке — если конвертация не лосслесс, подмены не происходит).

Конфиг (settings.json):
  "hooks": { "PostToolUse": [ { "matcher": "Read",
      "hooks": [ { "type": "command", "command": "python3 ~/.claude/hooks/jsonread_to_jtf.py" } ] } ] }

Хук получает JSON на stdin (tool_name, tool_input.file_path) и печатает в stdout
{"hookSpecificOutput": {"updatedToolOutput": ...}} — этим Claude Code заменяет
результат инструмента, который видит модель. Любая ошибка -> exit 0 без подмены
(чтение JSON не должно ломаться из-за хука).
"""

import json
import os
import sys

# конвертить только ощутимые файлы — на мелком JSON выигрыша нет
MIN_BYTES = 1024


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if event.get("tool_name") != "Read":
        sys.exit(0)
    path = (event.get("tool_input") or {}).get("file_path", "")
    if not isinstance(path, str) or not path.endswith(".json"):
        sys.exit(0)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        if len(raw) < MIN_BYTES:
            sys.exit(0)
        obj = json.loads(raw)
    except Exception:
        sys.exit(0)

    # импортируем вендоренный конвертер рядом с хуком
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from jtf import encode, decode
        compact = encode(obj)
        if decode(compact) != obj:        # подменяем ТОЛЬКО при лосслесс-конвертации
            sys.exit(0)
    except Exception:
        sys.exit(0)

    # не подменяем, если компактнее не стало (бывает на мелком/уникальном JSON)
    if len(compact) >= len(raw):
        sys.exit(0)

    note = (
        "[Содержимое .json показано в формате JTF — компактная замена JSON для "
        "экономии токенов. Данные те же, структура сохранена. Что такое JTF и как "
        "читать: github.com/k1y0miiii/json-token-skill. Редактировать файл "
        "(Edit/Write) нужно как обычный JSON — на диске он не менялся.]\n\n"
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "updatedToolOutput": note + compact,
            "additionalContext": "JSON сконвертирован в JTF для экономии токенов.",
        }
    }
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
