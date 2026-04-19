"""Tests for logslice.aliaser."""
import json
import pytest
from logslice.aliaser import (
    delete_alias,
    get_alias,
    list_aliases,
    load_aliases,
    save_aliases,
    set_alias,
)


@pytest.fixture()
def alias_file(tmp_path):
    return str(tmp_path / "aliases.json")


def test_load_missing_file_returns_empty(alias_file):
    import os
    assert not os.path.exists(alias_file)
    assert load_aliases(alias_file) == {}


def test_save_and_load_roundtrip(alias_file):
    data = {"errors": ["--level", "ERROR"], "last-hour": ["--start", "-1h"]}
    save_aliases(data, alias_file)
    loaded = load_aliases(alias_file)
    assert loaded == data


def test_load_invalid_json_type(alias_file):
    with open(alias_file, "w") as fh:
        json.dump(["not", "a", "dict"], fh)
    with pytest.raises(ValueError, match="JSON object"):
        load_aliases(alias_file)


def test_set_alias_creates_entry(alias_file):
    set_alias("myalias", ["--level", "WARN"], alias_file)
    assert get_alias("myalias", alias_file) == ["--level", "WARN"]


def test_set_alias_overwrites_existing(alias_file):
    set_alias("a", ["--start", "10:00"], alias_file)
    set_alias("a", ["--start", "11:00"], alias_file)
    assert get_alias("a", alias_file) == ["--start", "11:00"]


def test_set_alias_empty_name_raises(alias_file):
    with pytest.raises(ValueError, match="empty"):
        set_alias("", ["--level", "ERROR"], alias_file)


def test_get_alias_missing_raises(alias_file):
    with pytest.raises(KeyError, match="unknown"):
        get_alias("unknown", alias_file)


def test_delete_alias(alias_file):
    set_alias("temp", ["--tail", "50"], alias_file)
    delete_alias("temp", alias_file)
    assert "temp" not in list_aliases(alias_file)


def test_delete_alias_missing_raises(alias_file):
    with pytest.raises(KeyError):
        delete_alias("ghost", alias_file)


def test_list_aliases_returns_all(alias_file):
    set_alias("a", ["--level", "ERROR"], alias_file)
    set_alias("b", ["--start", "09:00"], alias_file)
    result = list_aliases(alias_file)
    assert set(result.keys()) == {"a", "b"}
