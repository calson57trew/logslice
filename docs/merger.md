# Log Merger

The `merger` module allows you to combine log lines from multiple files or
streams into a single ordered output.

## Features

- **Timestamp-based sorting** — lines are interleaved by their parsed timestamp
  so the resulting stream is chronologically ordered.
- **Source labelling** — optionally prefix every line with the filename or
  stream name it came from.
- **Continuation line handling** — lines without a recognisable timestamp are
  treated as untimed and emitted before the sorted timestamped block.

## CLI Usage

```bash
# Merge two files, sorted by timestamp
logslice main.log --merge secondary.log

# Merge without re-sorting (concatenate in source order)
logslice main.log --merge secondary.log --no-merge-sort

# Label each line with its source file
logslice main.log --merge secondary.log --merge-label
```

## Python API

```python
from logslice.merger import merge_logs, merge_files

# From in-memory lists
result = list(merge_logs([source_a, source_b], sort=True, label=False))

# From file paths
result = list(merge_files(["app.log", "db.log"], sort=True, label=True))
```

## Arguments

| Flag | Default | Description |
|---|---|---|
| `--merge FILE [FILE ...]` | — | Extra files to merge with primary input |
| `--merge-sort / --no-merge-sort` | `True` | Sort output by timestamp |
| `--merge-label` | `False` | Prefix lines with source name |
