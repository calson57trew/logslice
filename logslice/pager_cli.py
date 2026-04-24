"""CLI helpers for paginated output in logslice."""

import argparse
from typing import List, Optional

from logslice.paginator import paginate_lines, page_count, page_info


def add_pagination_args(parser: argparse.ArgumentParser) -> None:
    """Attach --page and --page-size arguments to an existing parser."""
    group = parser.add_argument_group("pagination")
    group.add_argument(
        "--page",
        type=int,
        default=None,
        metavar="N",
        help="Page number to display (1-indexed). Requires --page-size.",
    )
    group.add_argument(
        "--page-size",
        type=int,
        default=50,
        metavar="N",
        help="Number of lines per page (default: 50).",
    )


def apply_pagination(
    lines: List[str],
    page: Optional[int],
    page_size: int,
    verbose: bool = False,
) -> List[str]:
    """Return paginated slice of lines; optionally print page metadata."""
    if page is None:
        return lines

    if page_size <= 0:
        raise ValueError("--page-size must be a positive integer")
    if page < 1:
        raise ValueError("--page must be >= 1")

    total = len(lines)
    total_pages = page_count(total, page_size)
    if page > total_pages:
        raise ValueError(
            f"--page {page} is out of range: only {total_pages} page(s) available "
            f"for {total} lines with page-size {page_size}"
        )

    result = paginate_lines(lines, page_size=page_size, page=page)

    if verbose:
        info = page_info(total, page_size, page)
        print(
            f"# Page {info['page']}/{info['total_pages']} "
            f"({total} lines total, {page_size} per page)"
        )

    return result
