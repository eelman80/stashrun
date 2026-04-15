"""Tests for stashrun/cli_audit.py"""

from __future__ import annotations

import argparse

import pytest

from stashrun.cli_audit import cmd_audit_clear, cmd_audit_log, register_audit_commands
from stashrun.snapshots_audit import record_audit


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"name": None, "action": None, "limit": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_audit_log_empty(capsys):
    cmd_audit_log(_ns())
    out = capsys.readouterr().out
    assert "No audit entries found" in out


def test_cmd_audit_log_shows_entries(capsys):
    record_audit("save", "snap-x", user="bob")
    cmd_audit_log(_ns())
    out = capsys.readouterr().out
    assert "save" in out
    assert "snap-x" in out
    assert "bob" in out


def test_cmd_audit_log_filter_by_name(capsys):
    record_audit("save", "snap-x")
    record_audit("save", "snap-y")
    cmd_audit_log(_ns(name="snap-x"))
    out = capsys.readouterr().out
    assert "snap-x" in out
    assert "snap-y" not in out


def test_cmd_audit_log_limit(capsys):
    for i in range(5):
        record_audit("save", f"snap-{i}")
    cmd_audit_log(_ns(limit=2))
    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 2


def test_cmd_audit_clear_all(capsys):
    record_audit("save", "snap-a")
    record_audit("save", "snap-b")
    cmd_audit_clear(_ns())
    out = capsys.readouterr().out
    assert "2" in out


def test_cmd_audit_clear_by_name(capsys):
    record_audit("save", "snap-a")
    record_audit("save", "snap-b")
    cmd_audit_clear(_ns(name="snap-a"))
    out = capsys.readouterr().out
    assert "snap-a" in out
    assert "1" in out


def test_register_audit_commands():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_audit_commands(sub)
    args = parser.parse_args(["audit-log", "--limit", "5"])
    assert args.limit == 5
    args2 = parser.parse_args(["audit-clear", "--name", "mysnap"])
    assert args2.name == "mysnap"
