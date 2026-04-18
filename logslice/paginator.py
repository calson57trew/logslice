"""Pagination support for logslice output."""

from typing import Iterator, List


def paginate_lines(lines: List[str], page_size: int, page: int) -> List[str]:
    """Return a specific page of lines (1-indexed)."""
    if page_size <= 0:
        raise ValueError("page_size must be a positive integer")
    if page < 1:
        raise ValueError("page must be >= 1")
    start = (page - 1) * page_size
    end = start + page_size
    return lines[start:end]


def page_count(total_lines: int, page_size: int) -> int:
    """Return total number of pages for given line count and page size."""
    if page_size <= 0:
        raise ValueError("page_size must be a positive integer")
    if total_lines == 0:
        return 0
    return (total_lines + page_size - 1) // page_size


def iter_pages(lines: List[str], page_size: int) -> Iterator[List[str]]:
    """Yield successive pages of lines."""
    if page_size <= 0:
        raise ValueError("page_size must be a positive integer")
    for start in range(0, len(lines), page_size):
        yield lines[start:start + page_size]


def page_info(total_lines: int, page_size: int, page: int) -> dict:
    """Return metadata about the current page."""
    total = page_count(total_lines, page_size)
    return {
        "page": page,
        "page_size": page_size,
        "total_lines": total_lines,
        "total_pages": total,
        "has_prev": page > 1,
        "has_next": page < total,
    }
