"""Tests for logslice/archiver.py."""

import gzip
import io
import zipfile

import pytest

from logslice.archiver import (
    archive_to_gz,
    archive_to_zip,
    get_archiver,
    write_archive,
    count_archived,
)


SAMPLE = ["2024-01-01 INFO hello\n", "2024-01-01 ERROR boom\n"]


def test_archive_to_gz_produces_valid_gzip():
    data = archive_to_gz(SAMPLE)
    assert isinstance(data, bytes)
    with gzip.open(io.BytesIO(data), "rt") as f:
        content = f.read()
    assert "INFO hello" in content
    assert "ERROR boom" in content


def test_archive_to_gz_adds_newline_if_missing():
    data = archive_to_gz(["no newline"])
    with gzip.open(io.BytesIO(data), "rt") as f:
        content = f.read()
    assert content == "no newline\n"


def test_archive_to_zip_produces_valid_zip():
    data = archive_to_zip(SAMPLE)
    assert isinstance(data, bytes)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        assert "logslice.log" in names
        content = zf.read("logslice.log").decode()
    assert "INFO hello" in content
    assert "ERROR boom" in content


def test_archive_to_zip_custom_entry_name():
    data = archive_to_zip(SAMPLE, entry_name="output.log")
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        assert "output.log" in zf.namelist()


def test_archive_to_zip_adds_newline_if_missing():
    data = archive_to_zip(["no newline"])
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        content = zf.read("logslice.log").decode()
    assert content == "no newline\n"


def test_get_archiver_gz():
    fn = get_archiver("gz")
    assert fn is archive_to_gz


def test_get_archiver_zip():
    fn = get_archiver("zip")
    assert fn is archive_to_zip


def test_get_archiver_dot_prefix_stripped():
    fn = get_archiver(".gz")
    assert fn is archive_to_gz


def test_get_archiver_case_insensitive():
    fn = get_archiver("GZ")
    assert fn is archive_to_gz


def test_get_archiver_unknown_raises():
    with pytest.raises(ValueError, match="Unsupported archive format"):
        get_archiver("bz2")


def test_write_archive_gz(tmp_path):
    out = tmp_path / "out.gz"
    n = write_archive(SAMPLE, str(out), "gz")
    assert n > 0
    assert out.exists()
    with gzip.open(str(out), "rt") as f:
        assert "INFO hello" in f.read()


def test_write_archive_zip(tmp_path):
    out = tmp_path / "out.zip"
    n = write_archive(SAMPLE, str(out), "zip")
    assert n > 0
    assert out.exists()


def test_count_archived_returns_list():
    result = count_archived(iter(SAMPLE))
    assert result == SAMPLE
