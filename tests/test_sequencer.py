"""Tests for logslice.sequencer."""
import pytest
from logslice.sequencer import (
    SequenceGap,
    SequenceResult,
    check_sequence,
    extract_seq,
    format_sequence_report,
    iter_gap_lines,
)


# ---------------------------------------------------------------------------
# extract_seq
# ---------------------------------------------------------------------------

def test_extract_seq_key_equals():
    assert extract_seq("2024-01-01 seq=42 message") == 42


def test_extract_seq_key_colon():
    assert extract_seq("INFO seq:7 something happened") == 7


def test_extract_seq_hash_prefix():
    assert extract_seq("#100 some log line") == 100


def test_extract_seq_case_insensitive():
    assert extract_seq("SEQUENCE=5 data") == 5


def test_extract_seq_no_match_returns_none():
    assert extract_seq("plain log line without number") is None


def test_extract_seq_returns_first_match():
    # Two sequence-like tokens – first wins
    assert extract_seq("seq=3 seq=9") == 3


# ---------------------------------------------------------------------------
# check_sequence – no gaps
# ---------------------------------------------------------------------------

def test_no_gaps_clean_sequence():
    lines = [f"seq={i} ok\n" for i in range(1, 6)]
    result = check_sequence(lines)
    assert result.gap_count == 0
    assert result.sequenced_lines == 5
    assert result.total_lines == 5


def test_lines_without_seq_counted_but_not_sequenced():
    lines = ["no seq here\n", "seq=1 ok\n", "seq=2 ok\n"]
    result = check_sequence(lines)
    assert result.total_lines == 3
    assert result.sequenced_lines == 2
    assert result.gap_count == 0


# ---------------------------------------------------------------------------
# check_sequence – gaps detected
# ---------------------------------------------------------------------------

def test_single_gap_detected():
    lines = ["seq=1\n", "seq=2\n", "seq=5\n"]
    result = check_sequence(lines)
    assert result.gap_count == 1
    gap = result.gaps[0]
    assert gap.expected == 3
    assert gap.found == 5
    assert gap.missing == 2


def test_multiple_gaps():
    lines = ["seq=0\n", "seq=2\n", "seq=5\n"]
    result = check_sequence(lines)
    assert result.gap_count == 2


def test_custom_step():
    lines = ["seq=0\n", "seq=2\n", "seq=4\n"]
    result = check_sequence(lines, step=2)
    assert result.gap_count == 0


def test_custom_step_gap():
    lines = ["seq=0\n", "seq=4\n"]
    result = check_sequence(lines, step=2)
    assert result.gap_count == 1
    assert result.gaps[0].expected == 2


# ---------------------------------------------------------------------------
# ignore_reset
# ---------------------------------------------------------------------------

def test_reset_flagged_when_ignore_reset_false():
    lines = ["seq=10\n", "seq=1\n"]
    result = check_sequence(lines, ignore_reset=False)
    assert result.gap_count == 1


def test_reset_ignored_when_flag_set():
    lines = ["seq=10\n", "seq=1\n", "seq=2\n"]
    result = check_sequence(lines, ignore_reset=True)
    assert result.gap_count == 0


# ---------------------------------------------------------------------------
# iter_gap_lines & format_sequence_report
# ---------------------------------------------------------------------------

def test_iter_gap_lines_yields_description():
    lines = ["seq=1\n", "seq=3\n"]
    result = check_sequence(lines)
    gap_lines = list(iter_gap_lines(result))
    assert len(gap_lines) == 1
    assert "GAP" in gap_lines[0]
    assert "expected seq 2" in gap_lines[0]


def test_format_sequence_report_contains_counts():
    lines = ["seq=1\n", "seq=3\n", "no seq\n"]
    result = check_sequence(lines)
    report = format_sequence_report(result)
    assert "total lines    : 3" in report
    assert "sequenced lines: 2" in report
    assert "gaps detected  : 1" in report
