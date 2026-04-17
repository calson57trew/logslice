"""Command-line interface for logslice."""

import sys
import argparse
from typing import Optional

from logslice.slicer import slice_logs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='logslice',
        description='Filter and extract log lines by timestamp range.',
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Log file to read (defaults to stdin)',
    )
    parser.add_argument(
        '--start', '-s',
        metavar='TIMESTAMP',
        help='Include lines at or after this timestamp (e.g. "2024-01-15 10:00:00")',
    )
    parser.add_argument(
        '--end', '-e',
        metavar='TIMESTAMP',
        help='Include lines at or before this timestamp',
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.start and not args.end:
        parser.error('At least one of --start or --end must be provided.')

    try:
        if args.file:
            with open(args.file, 'r', encoding='utf-8', errors='replace') as fh:
                for line in slice_logs(fh, start=args.start, end=args.end):
                    sys.stdout.write(line)
        else:
            for line in slice_logs(sys.stdin, start=args.start, end=args.end):
                sys.stdout.write(line)
    except ValueError as exc:
        print(f'logslice: error: {exc}', file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f'logslice: error: file not found: {args.file}', file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
