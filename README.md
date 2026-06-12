# json-token-skill

**English** · [Русский](README.ru.md)

Claude Code skill and hook that make the agent read JSON as JTF — a lossless, compact
form that uses fewer tokens. Companion to
[json-token-format](https://github.com/k1y0miiii/json-token-format) (the converter and
spec).

There are two parts; install one or both.

## 1. Hook — automatic conversion on read

A `PostToolUse` hook on the `Read` tool. When the agent reads a `.json` file, the hook
converts the content to JTF and substitutes it as the tool result the agent sees
(`hookSpecificOutput.updatedToolOutput`). The agent gets the compact version, so the
raw JSON never enters the context window.

Safeguards built into the hook:
- Only files ending in `.json`, and only when larger than 1 KB.
- The conversion is verified lossless (`decode(encode(x)) == x`) before substituting;
  if not, the raw JSON is left untouched.
- If the JTF is not actually shorter than the JSON, no substitution happens.
- Any error exits quietly — a hook failure never breaks reading a file.

Install (default target `~/.claude`):

```sh
./install.sh
```

It copies the skill to `~/.claude/skills/json-token-format/`, the hook to
`~/.claude/hooks/`, then prints the `hooks` block to add to `~/.claude/settings.json`.
Merge it with any hooks you already have:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Read",
        "hooks": [ { "type": "command", "command": "python3 ~/.claude/hooks/jsonread_to_jtf.py" } ] }
    ]
  }
}
```

The hook starts working in the next session. For a single project instead of globally,
put the same block in the project's `.claude/settings.json` and point the command at
the hook wherever you keep it.

## 2. Skill — teaches the agent to read JTF and convert by hand

`skill/SKILL.md` is a Claude Code skill. It explains how to read JTF and how to run the
converter, so the agent can convert large JSON itself even without the hook. `install.sh`
copies it to `~/.claude/skills/`.

## Cursor

Cursor has no hook system. Use the rule in `.cursor/rules/json-token.mdc`: it tells the
agent to convert large JSON with `python3 jtf.py encode file.json` and read the JTF.
Cursor's rule format changes between versions — if the `.mdc` is not picked up, paste
the guidance into `AGENTS.md` instead.

## What JTF looks like

```
name=example
count=3
items:
  #3 id status
      1   active
      2   pending
      3   active
```

The same data in JSON is longer in tokens. Full spec, grammar, and benchmark:
[json-token-format](https://github.com/k1y0miiii/json-token-format).

## Limitations

- The hook changes only what `Read` shows. Editing works on the real JSON file
  (`Edit`/`Write` are unaffected) — so if you edit a JSON you just read as JTF, match
  against the actual JSON, not the JTF view.
- JTF pays off on large or repetitive JSON. On small or all-unique documents the hook
  detects there is no gain and leaves the JSON as is.
- `hookSpecificOutput.updatedToolOutput` requires a recent Claude Code version. If your
  version does not support it, use the skill (part 2) and convert manually.
