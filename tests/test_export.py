"""Tests for stashrun.export module."""

import json
import os
import pytest
from pathlib import Path

from stashrun.export import export_snapshot, import_snapshot, _parse_dotenv
from stashrun.storage import load_snapshot, save_snapshot


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    stash_dir = tmp_path / ".stashrun"
    stash_dir.mkdir()
    monkeypatch.setenv("STASHRUN_DIR", str(stash_dir))
    return stash_dir


SAMPLE_ENV = {"APP_ENV": "production", "DB_URL": "postgres://localhost/db", "SECRET": 'p@ss"word'}


def test_export_json_creates_file(isolated_stash_dir, tmp_path):
    save_snapshot("mysnap", SAMPLE_ENV)
    out = tmp_path / "export.json"
    result = export_snapshot("mysnap", str(out))
    assert result is True
    assert out.exists()


def test_export_json_content(isolated_stash_dir, tmp_path):
    save_snapshot("mysnap", SAMPLE_ENV)
    out = tmp_path / "export.json"
    export_snapshot("mysnap", str(out))
    loaded = json.loads(out.read_text())
    assert loaded == SAMPLE_ENV


def test_export_dotenv_content(isolated_stash_dir, tmp_path):
    save_snapshot("mysnap", {"KEY": "value", "OTHER": "hello"})
    out = tmp_path / "export.env"
    export_snapshot("mysnap", str(out), fmt="dotenv")
    content = out.read_text()
    assert 'KEY="value"' in content
    assert 'OTHER="hello"' in content


def test_export_missing_snapshot_returns_false(isolated_stash_dir, tmp_path):
    out = tmp_path / "export.json"
    result = export_snapshot("nonexistent", str(out))
    assert result is False
    assert not out.exists()


def test_import_json_restores_snapshot(isolated_stash_dir, tmp_path):
    src = tmp_path / "import.json"
    src.write_text(json.dumps(SAMPLE_ENV))
    result = import_snapshot("imported", str(src))
    assert result is True
    assert load_snapshot("imported") == SAMPLE_ENV


def test_import_dotenv_restores_snapshot(isolated_stash_dir, tmp_path):
    src = tmp_path / "import.env"
    src.write_text('APP_ENV="staging"\nPORT="8080"\n')
    result = import_snapshot("imported", str(src), fmt="dotenv")
    assert result is True
    data = load_snapshot("imported")
    assert data["APP_ENV"] == "staging"
    assert data["PORT"] == "8080"


def test_import_missing_file_returns_false(isolated_stash_dir, tmp_path):
    result = import_snapshot("snap", str(tmp_path / "missing.json"))
    assert result is False


def test_import_invalid_json_returns_false(isolated_stash_dir, tmp_path):
    src = tmp_path / "bad.json"
    src.write_text("not valid json{{{")
    result = import_snapshot("snap", str(src))
    assert result is False


def test_parse_dotenv_handles_comments_and_blanks():
    content = "# comment\n\nKEY=\"value\"\n"
    result = _parse_dotenv(content)
    assert result == {"KEY": "value"}


def test_parse_dotenv_escaped_quotes():
    content = 'SECRET="p@ss\\"word"\n'
    result = _parse_dotenv(content)
    assert result["SECRET"] == 'p@ss"word'
