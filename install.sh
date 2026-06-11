#!/usr/bin/env bash
# Ставит скилл и PostToolUse-хук в каталог Claude Code (по умолчанию ~/.claude).
# settings.json не трогает — печатает фрагмент, который нужно добавить вручную.
set -euo pipefail
cd "$(dirname "$0")"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

mkdir -p "$CLAUDE_DIR/skills/json-token-format" "$CLAUDE_DIR/hooks"
cp skill/SKILL.md "$CLAUDE_DIR/skills/json-token-format/SKILL.md"
cp jtf.py        "$CLAUDE_DIR/skills/json-token-format/jtf.py"
cp hooks/jsonread_to_jtf.py "$CLAUDE_DIR/hooks/jsonread_to_jtf.py"
cp hooks/jtf.py             "$CLAUDE_DIR/hooks/jtf.py"

echo "Установлено в $CLAUDE_DIR :"
echo "  skills/json-token-format/SKILL.md"
echo "  hooks/jsonread_to_jtf.py (+ jtf.py)"
echo
echo "Чтобы включить авто-конвертацию при чтении .json, добавьте в"
echo "$CLAUDE_DIR/settings.json блок hooks (объедините со своим, если он уже есть):"
echo "----------------------------------------------------------------------"
cat settings.example.json
echo "----------------------------------------------------------------------"
echo "Скилл подхватится сам. Хук начнёт работать после перезапуска сессии."
