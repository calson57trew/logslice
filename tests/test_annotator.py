"""Tests for logslice.annotator."""
import pytest
from logslice.annotator import annotate_line, annotate_lines, count_annotated


def test_annotate_line_prepend():
    result = annotate_line('some log message\n', 'APP')
    assert result == '[APP] some log message\n'


def test_annotate_line_no_trailing_newline():
    result = annotate_line('some log message', 'SVC')
    assert result == '[SVC] some log message'


def test_annotate_line_inline_with_timestamp():
    line = '2024-01-15T10:00:00 INFO starting\n'
    result = annotate_line(line, 'APP', inline=True)
    assert result.startswith('2024-01-15T10:00:00 [APP]')
    assert 'INFO starting' in result


def test_annotate_line_inline_no_timestamp_falls_back_to_prepend():
    line = 'no timestamp here\n'
    result = annotate_line(line, 'TAG', inline=True)
    assert result == '[TAG] no timestamp here\n'


def test_annotate_lines_all_timestamped():
    lines = [
        '2024-01-15T10:00:00 INFO first\n',
        '2024-01-15T10:00:01 ERROR second\n',
    ]
    out = list(annotate_lines(lines, 'SVC'))
    assert all(l.startswith('[SVC]') for l in out)


def test_annotate_lines_skip_continuations():
    lines = [
        '2024-01-15T10:00:00 INFO first\n',
        '  continuation of first\n',
        '2024-01-15T10:00:01 INFO second\n',
    ]
    out = list(annotate_lines(lines, 'X', skip_continuations=True))
    assert out[0].startswith('[X]')
    assert out[1] == '  continuation of first\n'  # unchanged
    assert out[2].startswith('[X]')


def test_annotate_lines_no_skip_continuations():
    lines = [
        '2024-01-15T10:00:00 INFO first\n',
        '  continuation\n',
    ]
    out = list(annotate_lines(lines, 'X', skip_continuations=False))
    assert out[1].startswith('[X]')


def test_count_annotated():
    original = ['line one\n', 'line two\n']
    annotated = ['[T] line one\n', 'line two\n']
    assert count_annotated(original, annotated) == 1


def test_count_annotated_all_same():
    lines = ['abc\n', 'def\n']
    assert count_annotated(lines, lines[:]) == 0
