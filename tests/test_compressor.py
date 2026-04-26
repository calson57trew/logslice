"""Tests for logslice.compressor."""
import pytest

from logslice.compressor import (
    CompressedLine,
    compress_lines,
    count_compressed,
)


# ---------------------------------------------------------------------------
# CompressedLine.render
# ---------------------------------------------------------------------------

def test_render_single_no_prefix():
    cl = CompressedLine(line="hello\n", count=1)
    assert cl.render() == "hello\n"


def test_render_repeated_adds_prefix():
    cl = CompressedLine(line="hello\n", count=5)
    assert cl.render() == "[x5] hello\n"


def test_render_show_count_false_hides_prefix():
    cl = CompressedLine(line="hello\n", count=5)
    assert cl.render(show_count=False) == "hello\n"


def test_render_adds_newline_if_missing():
    cl = CompressedLine(line="no newline", count=1)
    assert cl.render().endswith("\n")


# ---------------------------------------------------------------------------
# compress_lines — consecutive mode (default)
# ---------------------------------------------------------------------------

def _lines(raw):
    return [l + "\n" for l in raw]


def test_consecutive_no_repeats_passthrough():
    src = _lines(["a", "b", "c"])
    result = list(compress_lines(src))
    assert [r.line for r in result] == src
    assert all(r.count == 1 for r in result)


def test_consecutive_collapses_run():
    src = _lines(["a", "b", "b", "b", "c"])
    result = list(compress_lines(src))
    assert len(result) == 3
    assert result[1].count == 3
    assert result[1].line == "b\n"


def test_consecutive_below_min_repeat_not_collapsed():
    src = _lines(["a", "b", "b", "c"])
    # min_repeat=2 means a pair IS collapsed
    result = list(compress_lines(src, min_repeat=2))
    assert len(result) == 3
    assert result[1].count == 2


def test_consecutive_min_repeat_3_pair_not_collapsed():
    src = _lines(["a", "b", "b", "c"])
    result = list(compress_lines(src, min_repeat=3))
    # pair should NOT be collapsed
    assert len(result) == 4
    assert all(r.count == 1 for r in result)


def test_consecutive_non_adjacent_duplicates_not_merged():
    src = _lines(["a", "b", "a", "a"])
    result = list(compress_lines(src, consecutive_only=True))
    # first 'a' is alone; second run of 'a' is 2
    assert result[0].count == 1
    assert result[0].line == "a\n"
    assert result[2].count == 2


# ---------------------------------------------------------------------------
# compress_lines — global mode
# ---------------------------------------------------------------------------

def test_global_merges_non_adjacent():
    src = _lines(["a", "b", "a", "a"])
    result = list(compress_lines(src, consecutive_only=False, min_repeat=2))
    # 'a' appears 3 times globally → one CompressedLine(count=3)
    a_entries = [r for r in result if r.line == "a\n"]
    assert len(a_entries) == 1
    assert a_entries[0].count == 3


def test_global_unique_lines_passthrough():
    src = _lines(["x", "y", "z"])
    result = list(compress_lines(src, consecutive_only=False))
    assert all(r.count == 1 for r in result)


# ---------------------------------------------------------------------------
# Invalid arguments
# ---------------------------------------------------------------------------

def test_min_repeat_less_than_2_raises():
    with pytest.raises(ValueError, match="min_repeat"):
        list(compress_lines(_lines(["a"]), min_repeat=1))


# ---------------------------------------------------------------------------
# count_compressed
# ---------------------------------------------------------------------------

def test_count_compressed_returns_savings():
    src = _lines(["err", "err", "err", "ok"])
    saved = count_compressed(src, consecutive_only=True, min_repeat=2)
    # 4 lines → 2 output lines; saved = 2
    assert saved == 2


def test_count_compressed_no_duplicates_zero():
    src = _lines(["a", "b", "c"])
    assert count_compressed(src) == 0
