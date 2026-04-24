"""archiver.py — compress and archive sliced log output to gzip or zip."""

import gzip
import io
import zipfile
from typing import Iterable, List


SUPPORTED_FORMATS = ("gz", "zip")


def archive_to_gz(lines: Iterable[str]) -> bytes:
    """Compress an iterable of log lines into gzip bytes."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        for line in lines:
            if not line.endswith("\n"):
                line = line + "\n"
            gz.write(line.encode())
    return buf.getvalue()


def archive_to_zip(lines: Iterable[str], entry_name: str = "logslice.log") -> bytes:
    """Compress an iterable of log lines into a zip archive bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        content = "".join(
            line if line.endswith("\n") else line + "\n" for line in lines
        )
        zf.writestr(entry_name, content)
    return buf.getvalue()


def get_archiver(fmt: str):
    """Return the archive function for the given format string.

    Raises ValueError for unsupported formats.
    """
    fmt = fmt.lower().lstrip(".")
    if fmt == "gz":
        return archive_to_gz
    if fmt == "zip":
        return archive_to_zip
    raise ValueError(
        f"Unsupported archive format: {fmt!r}. Choose from: {', '.join(SUPPORTED_FORMATS)}"
    )


def write_archive(lines: Iterable[str], path: str, fmt: str) -> int:
    """Archive *lines* to *path* using *fmt*. Returns number of bytes written."""
    archiver = get_archiver(fmt)
    data = archiver(lines)
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)


def count_archived(lines: Iterable[str]) -> List[str]:
    """Pass-through helper that materialises lines for downstream use."""
    return list(lines)
