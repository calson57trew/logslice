"""Tests for logslice.paginator."""

import pytest
from logslice.paginator import paginate_lines, page_count, iter_pages, page_info

LINES = [f"line {i}\n" for i in range(1, 11)]  # 10 lines


def test_paginate_first_page():
    result = paginate_lines(LINES, page_size=3, page=1)
    assert result == ["line 1\n", "line 2\n", "line 3\n"]


def test_paginate_second_page():
    result = paginate_lines(LINES, page_size=3, page=2)
    assert result == ["line 4\n", "line 5\n", "line 6\n"]


def test_paginate_last_partial_page():
    result = paginate_lines(LINES, page_size=3, page=4)
    assert result == ["line 10\n"]


def test_paginate_beyond_end_returns_empty():
    result = paginate_lines(LINES, page_size=3, page=10)
    assert result == []


def test_paginate_invalid_page_size():
    with pytest.raises(ValueError):
        paginate_lines(LINES, page_size=0, page=1)


def test_paginate_invalid_page():
    with pytest.raises(ValueError):
        paginate_lines(LINES, page_size=5, page=0)


def test_page_count_exact():
    assert page_count(9, 3) == 3


def test_page_count_with_remainder():
    assert page_count(10, 3) == 4


def test_page_count_zero_lines():
    assert page_count(0, 5) == 0


def test_iter_pages_yields_all():
    pages = list(iter_pages(LINES, page_size=4))
    assert len(pages) == 3
    assert pages[0] == LINES[:4]
    assert pages[2] == LINES[8:]


def test_iter_pages_empty_input():
    pages = list(iter_pages([], page_size=5))
    assert pages == []


def test_page_info_middle_page():
    info = page_info(total_lines=10, page_size=3, page=2)
    assert info["page"] == 2
    assert info["total_pages"] == 4
    assert info["has_prev"] is True
    assert info["has_next"] is True


def test_page_info_first_page():
    info = page_info(total_lines=10, page_size=5, page=1)
    assert info["has_prev"] is False
    assert info["has_next"] is True


def test_page_info_last_page():
    info = page_info(total_lines=10, page_size=5, page=2)
    assert info["has_prev"] is True
    assert info["has_next"] is False
