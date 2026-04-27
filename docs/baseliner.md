# Baseliner

The **baseliner** module lets you save a snapshot of "known" log messages and
then highlight only the *new* lines that appear in a subsequent run.

## How it works

1. Each log line is normalised (timestamps are stripped) to produce a stable
   fingerprint via `normalize_line` from `logslice.deduplicator`.
2. Fingerprints are stored in a JSON array on disk.
3. On the next run the current lines are compared against the saved set; only
   lines whose fingerprint is absent are forwarded.

## CLI flags

| Flag | Default | Description |
|------|---------|-------------|
| `--baseline-file PATH` | `None` | Path to the baseline JSON file. |
| `--baseline-save` | `False` | Overwrite the baseline with the current input. |
| `--baseline-summary` | `False` | Print a comparison summary to stderr. |
| `--baseline-emit-known` | `False` | Pass all lines through (not just new ones). |

## Typical workflow

```bash
# 1. Capture a clean baseline
logslice --baseline-file bl.json --baseline-save app.log

# 2. Next day – show only new messages
logslice --baseline-file bl.json app.log

# 3. Show a summary alongside the new lines
logslice --baseline-file bl.json --baseline-summary app.log
```

## Python API

```python
from logslice.baseliner import load_baseline, save_baseline, compare_to_baseline

# Save
save_baseline("bl.json", open("app.log"))

# Compare
baseline = load_baseline("bl.json")
result = compare_to_baseline(open("app.log"), baseline)
for line in result.new_lines:
    print(line, end="")
```

## Notes

- The baseline file is a plain JSON array; it can be committed to version
  control alongside your project.
- Fingerprinting is case-sensitive but timestamp-agnostic, so the same message
  at a different time is still considered *known*.
