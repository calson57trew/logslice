"""Tests for logslice.summarizer."""

from logslice.summarizer import summarize_lines, format_summary, LogSummary


SAMPLE_LINES = [
    "2024-01-01T10:00:00 INFO  service started\n",
    "2024-01-01T10:00:01 DEBUG loading config\n",
    "2024-01-01T10:00:02 ERROR failed to connect\n",
    "    traceback line (continuation)\n",
    "2024-01-01T10:00:03 WARN  retrying\n",
    "2024-01-01T10:00:04 ERROR timeout\n",
]


def test_total_lines():
    s = summarize_lines(SAMPLE_LINES)
    assert s.total_lines == 6


def test_level_counts():
    s = summarize_lines(SAMPLE_LINES)
    assert s.level_counts["ERROR"] == 2
    assert s.level_counts["INFO"] == 1
    assert s.level_counts["DEBUG"] == 1
    assert s.level_counts["WARN"] == 1


def test_first_and_last_timestamp():
    s = summarize_lines(SAMPLE_LINES)
    assert s.first_timestamp is not None
    assert "10:00:00" in s.first_timestamp
    assert s.last_timestamp is not None
    assert "10:00:04" in s.last_timestamp


def test_no_timestamp_lines():
    lines = ["INFO something happened\n", "DEBUG detail\n"]
    s = summarize_lines(lines)
    assert s.first_timestamp is None
    assert s.last_timestamp is None


def test_unique_messages_deduped():
    lines = [
        "2024-01-01T10:00:00 ERROR disk full\n",
        "2024-01-01T10:00:01 ERROR disk full\n",
    ]
    s = summarize_lines(lines)
    assert s.unique_messages == 1


def test_empty_input():
    s = summarize_lines([])
    assert s.total_lines == 0
    assert s.matched_lines == 0
    assert s.level_counts == {}


def test_format_summary_contains_keys():
    s = LogSummary(total_lines=10, matched_lines=5, unique_messages=3,
                   first_timestamp="2024-01-01T10:00:00",
                   last_timestamp="2024-01-01T11:00:00",
                   level_counts={"ERROR": 2, "INFO": 3})
    output = format_summary(s)
    joined = "\n".join(output)
    assert "Total lines" in joined
    assert "ERROR" in joined
    assert "INFO" in joined
    assert "2024-01-01T10:00:00" in joined


def test_format_summary_no_levels():
    s = LogSummary(total_lines=2)
    output = format_summary(s)
    assert not any("breakdown" in l for l in output)
