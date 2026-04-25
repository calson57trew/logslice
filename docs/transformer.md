# Transformer

The **transformer** module applies line-level text mutations to log output.
Transforms are composable and applied in the order they are specified.

## Supported Operations

| Operation | CLI Flag | Description |
|-----------|----------|-------------|
| `upper`   | `--upper` | Convert every character to uppercase |
| `lower`   | `--lower` | Convert every character to lowercase |
| `strip`   | `--strip` | Remove leading and trailing whitespace |
| `replace` | `--replace PATTERN REPLACEMENT` | Substitute regex matches (repeatable) |

## CLI Usage

```bash
# Uppercase all lines
logslice --upper app.log

# Replace all numbers with a placeholder
logslice --replace '\d+' NUM app.log

# Case-insensitive replacement
logslice --replace 'error' ERR --transform-ignore-case app.log

# Chain: strip whitespace then lowercase
logslice --strip --lower app.log

# Multiple replacements
logslice --replace '\d+' NUM --replace 'ERROR' ERR app.log
```

## Python API

```python
from logslice.transformer import compile_transforms, transform_lines

ops = [
    ("strip",),
    ("replace", r"\d+", "NUM"),
    ("lower",),
]
transforms = compile_transforms(ops, ignore_case=False)
result = list(transform_lines(open("app.log"), transforms))
```

## Notes

- Transforms are applied **left to right** (or top to bottom in the CLI).
- `--upper` and `--lower` together will result in lowercase (lower is last).
- The `--replace` flag can be repeated; each repetition adds another
  substitution stage in the pipeline.
- `--transform-ignore-case` applies only to `--replace` patterns.
