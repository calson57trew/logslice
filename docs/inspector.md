# logslice inspector

The `inspector` module scans a stream of log lines and reports structural
metadata without modifying the stream.

## What it reports

| Field | Description |
|---|---|
| `total_lines` | Total number of lines scanned |
| `timed_lines` | Lines that contain a recognised timestamp |
| `timestamp_formats` | Detected formats (`iso8601`, `epoch`) with occurrence counts |
| `levels` | Log-level keywords found (`DEBUG`, `INFO`, `WARN`, `ERROR`, …) |
| `kv_fields (top10)` | Most frequent `key=value` field names |
| `samples` | First *N* lines (default 5) for quick visual inspection |

## CLI usage

Add `--inspect` to any `logslice` invocation to print the report instead of
the filtered lines:

```bash
logslice --from 2024-03-15T10:00:00 --inspect app.log
```

Control the number of sample lines shown:

```bash
logslice --inspect --inspect-samples 10 app.log
```

## Python API

```python
from logslice.inspector import inspect_lines, format_inspect

with open("app.log") as fh:
    result = inspect_lines(fh, max_samples=5)

print(format_inspect(result))
# total_lines      : 4821
# timed_lines      : 4817
# timestamp_formats: iso8601(4817)
# levels           : DEBUG=312, ERROR=45, INFO=4312, WARN=152
# kv_fields (top10): request_id(4817), status(3201), user(2100), ...
```

## Notes

- `WARNING` is normalised to `WARN` in the level counts.
- Epoch timestamps are detected as 10-digit integers not adjacent to other
  digits, so they are not confused with IDs or port numbers.
- The inspector never modifies or filters lines; `apply_inspect` returns an
  empty list only when `--inspect` is active so that downstream pipeline
  stages receive nothing (the report has already been written to stdout).
