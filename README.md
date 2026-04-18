# logslice

> CLI tool to filter and extract structured log ranges by timestamp or pattern

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
# Extract logs between two timestamps
logslice --start "2024-01-15 10:00:00" --end "2024-01-15 10:30:00" app.log

# Filter by pattern within a time range
logslice --start "2024-01-15 10:00:00" --pattern "ERROR" app.log

# Read from stdin
cat app.log | logslice --start "2024-01-15 10:00:00" --end "2024-01-15 11:00:00"

# Output to file
logslice --start "2024-01-15 10:00:00" --end "2024-01-15 10:30:00" app.log -o slice.log

# Show line numbers in output
logslice --start "2024-01-15 10:00:00" --end "2024-01-15 10:30:00" --line-numbers app.log
```

### Options

| Flag | Description |
|------|-------------|
| `--start` | Start timestamp or pattern |
| `--end` | End timestamp or pattern |
| `--pattern` | Regex pattern to match log lines |
| `--format` | Log timestamp format (default: auto-detect) |
| `--line-numbers` | Prefix each output line with its original line number |
| `-o, --output` | Write output to file instead of stdout |
| `-q, --quiet` | Suppress warnings and info messages |

---

## Requirements

- Python 3.8+

---

## License

MIT © [yourname](https://github.com/yourname)
