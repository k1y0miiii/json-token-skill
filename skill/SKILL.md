---
name: json-token-format
description: Use when reading, analysing, or showing large JSON files (configs, API responses, logs, arrays of records). Converts JSON to JTF — a compact, lossless format that uses fewer tokens — and explains how to read JTF.
---

# JSON Token Format (JTF)

JTF is a lossless, compact text form of JSON. It uses fewer tokens than JSON, so
reading large JSON as JTF leaves more room in the context window. `decode(encode(x))`
always equals `x`.

## When to use

- Reading or analysing a large `.json` file (arrays of objects, logs, API dumps).
- Showing JSON data back to the user compactly.
- Not worth it for tiny JSON (a few lines) — the savings are negligible.

## How to convert

The converter is `jtf.py` (pure standard library, no dependencies):

```sh
python3 jtf.py encode data.json        # JSON -> JTF (stdout)
python3 jtf.py decode data.jtf         # JTF -> JSON (stdout)
python3 jtf.py bench data.json         # token comparison (needs tiktoken)
```

If the PostToolUse hook from this repo is installed, reading a `.json` with the Read
tool already returns JTF automatically — you do not need to call the converter by hand.

## How to read JTF

- `key=value` — an object field with a primitive value.
- `key:` then indented lines — a nested object.
- `#N k1 k2 k3` then tab-separated rows — an array of N objects with the same keys
  (a table). Dotted keys like `addr.city` mean a nested object (`{"addr":{"city":...}}`).
- `[N] a,b,c` — an array of N primitives.
- `[N]` then `- item` lines — a mixed array.
- A leading `#dict:` block defines short aliases (`$0`, `$1`, …) for repeated string
  values; `$0` in the body means that value, `{$1}suffix` means prefix + suffix.
- Bare strings are literal; quoted strings follow JSON escaping. `null`/`true`/`false`
  and numbers are literal.

## Editing JSON

JTF is for reading. To edit a JSON file, treat the file on disk as normal JSON
(Edit/Write operate on the real JSON, not the JTF view).
