# Pivot — Time-Bucketed Pattern Frequency

The **pivot** feature counts how often a regex pattern appears inside configurable
time buckets, giving you a quick histogram of log activity over time.

## CLI flags

| Flag | Default | Description |
|---|---|---|
| `--pivot-pattern REGEX` | *(none)* | Pattern to count per bucket. Required to activate pivot. |
| `--pivot-bucket SECONDS` | `60` | Width of each time bucket in seconds. |
| `--pivot-top N` | `0` (all) | Only show the N busiest buckets. |
| `--pivot-ignore-case` | off | Case-insensitive pattern matching. |

## Example

```bash
logslice --from 2024-01-15T12:00:00 --to 2024-01-15T13:00:00 \
         --pivot-pattern ERROR --pivot-bucket 300 app.log
```

Sample output:

```
# pivot  pattern='ERROR'  bucket=300s
# total_lines=4821  matched=37

2024-01-15 12:00:00      12  ############
2024-01-15 12:05:00       3  ###
2024-01-15 12:15:00      22  ######################
```

## How it works

1. Each line is inspected for a recognised timestamp via `extract_timestamp`.
2. The timestamp is floored to the nearest bucket boundary
   (e.g. `12:07:33` → `12:05:00` for a 300 s bucket).
3. If the pattern matches the line, the current bucket counter is incremented.
4. Lines without a timestamp inherit the bucket of the most recent timestamped
   line (or fall into the special `(no timestamp)` bucket).

## Python API

```python
from logslice.pivot import build_pivot, format_pivot

with open("app.log") as fh:
    table = build_pivot(fh, pattern=r"ERROR", bucket_size=300)

for line in format_pivot(table, top_n=10):
    print(line)
```
