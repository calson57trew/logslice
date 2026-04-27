# Histogram

The `histogram` feature builds a frequency bar chart from log lines, bucketing
them by log level (default) or by a user-supplied regex pattern.

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--histogram [PATTERN]` | off | Enable histogram. Optionally supply a capturing regex. |
| `--histogram-bar-width N` | `40` | Width of the rendered bars in characters. |
| `--histogram-no-other` | off | Suppress the `(other)` bucket for unmatched lines. |
| `--histogram-only` | off | Emit only the histogram report; suppress normal output. |

## Default behaviour

When `--histogram` is given without a pattern, each line is matched against a
built-in level regex (`ERROR`, `WARN`, `WARNING`, `INFO`, `DEBUG`, `TRACE`,
`CRITICAL`, `FATAL`).  Lines that do not match any level are counted in an
`(other)` bucket unless `--histogram-no-other` is set.

## Custom patterns

Supply a regular expression to group by an arbitrary field:

```
logslice slice app.log --histogram '(user_\w+)'
```

If the pattern contains a capturing group the first group value is used as the
bucket key.  If there is no group the full match is used.

## Example output

```
ERROR  |########################################|  42
WARN   |####################--------------------|  21
INFO   |##########------------------------------|  10
(other)|#####-----------------------------------|   5
```

Bars are scaled so the most frequent bucket always fills the full `bar-width`.

## Python API

```python
from logslice.histogram import build_histogram, format_histogram

result = build_histogram(lines)
for row in format_histogram(result, bar_width=30):
    print(row, end="")
```
