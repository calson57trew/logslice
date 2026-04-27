# logslice indexer

The **indexer** module builds a lightweight byte-offset index over a log file,
enabling fast random-access slicing without scanning the entire file from the
beginning.

## How it works

1. `build_index(path)` reads every line of the file and records:
   - The **byte offset** of the line's first byte.
   - The **timestamp** extracted by `extract_timestamp` (or `None` for
     continuation lines).
   - The **line number** (0-based).

2. The resulting `LogIndex` can be saved to disk as JSON with `save_index` and
   reloaded later with `load_index`.

3. `seek_to_timestamp(index, ts)` performs a linear scan over the *timed*
   entries and returns the byte offset of the first line whose timestamp is
   **≥** the requested value.  Combined with `file.seek(offset)`, this lets
   you jump directly to the relevant section of a large log file.

## CLI flags

| Flag | Description |
|------|-------------|
| `--index-build LOG_FILE` | Build an index for `LOG_FILE` and write it to `--index-file` (defaults to `LOG_FILE.idx`). |
| `--index-file INDEX_FILE` | Path to the index file used by `--index-seek` and `--index-stats`. |
| `--index-seek TIMESTAMP` | Print the byte offset of the first line with timestamp ≥ `TIMESTAMP`. |
| `--index-stats` | Print `total`, `timed`, and `untimed` line counts for the loaded index. |

## Example

```bash
# Build the index once
logslice --index-build app.log --index-file app.idx
# Index written to app.idx: 42301 lines, 41889 timed.

# Find the byte offset for a specific timestamp
logslice --index-file app.idx --index-seek 2024-06-01T12:00:00
# 8473621

# Inspect index statistics
logslice --index-file app.idx --index-stats
# total: 42301
# timed: 41889
# untimed: 412
```

## Programmatic use

```python
from logslice.indexer import build_index, seek_to_timestamp

index = build_index("app.log")
offset = seek_to_timestamp(index, "2024-06-01T12:00:00")
if offset is not None:
    with open("app.log", "r") as fh:
        fh.seek(offset)
        for line in fh:
            print(line, end="")
```
