# Heatmap

The `--heatmap` flag renders a text bar-chart showing how many log lines fall
into each time bucket. This makes it easy to spot bursts of activity or quiet
periods at a glance.

## Usage

```
logslice --heatmap [--heatmap-bucket minute|hour]
         [--heatmap-pattern REGEX]
         [--heatmap-width N]
         <logfile>
```

### Flags

| Flag | Default | Description |
|---|---|---|
| `--heatmap` | off | Enable heatmap mode. Output is the chart; matched lines are not printed. |
| `--heatmap-bucket` | `minute` | Granularity: `minute` or `hour`. |
| `--heatmap-pattern` | *(none)* | Only count lines matching this regex in the buckets. |
| `--heatmap-width` | `40` | Character width of each bar. |

## Example

```
$ logslice --heatmap --heatmap-bucket hour app.log
2024-03-15T09  |########                                |  42
2024-03-15T10  |########################################|  210
2024-03-15T11  |######################                  |  115
2024-03-15T12  |#####                                   |  28
```

Filter to only error lines:

```
$ logslice --heatmap --heatmap-pattern 'ERROR|CRITICAL' app.log
2024-03-15T10:14  |####################                    |  5
2024-03-15T10:47  |########################################|  10
2024-03-15T11:03  |################                        |  4
```

## Programmatic API

```python
from logslice.heatmap import build_heatmap, format_heatmap

with open("app.log") as fh:
    result = build_heatmap(fh, bucket_size="minute", label_pattern=r"ERROR")

for row in format_heatmap(result, bar_width=50):
    print(row, end="")
```

`build_heatmap` returns a `HeatmapResult` with:

- `buckets` – ordered `dict` mapping bucket label → line count.
- `bucket_size` – the granularity used.
- `total_lines` – total lines consumed.
- `timed_lines` – lines that carried a recognised timestamp.
