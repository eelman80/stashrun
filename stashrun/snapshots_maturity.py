"""Track maturity level of snapshots (draft, stable, deprecated)."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir

VALID_LEVELS = {"draft", "stable", "deprecated"}
DEFAULT_LEVEL = "draft"


def _maturity_path() -> Path:
    return get_stash_dir() / "maturity.json"


def _load_maturity() -> dict:
    p = _maturity_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_maturity(data: dict) -> None:
    _maturity_path().write_text(json.dumps(data, indent=2))


def set_maturity(name: str, level: str) -> bool:
    if level not in VALID_LEVELS:
        return False
    data = _load_maturity()
    data[name] = level
    _save_maturity(data)
    return True


def get_maturity(name: str, default: str = DEFAULT_LEVEL) -> str:
    return _load_maturity().get(name, default)


def remove_maturity(name: str) -> bool:
    data = _load_maturity()
    if name not in data:
        return False
    del data[name]
    _save_maturity(data)
    return True


def list_maturity() -> dict:
    return _load_maturity()


def find_by_maturity(level: str) -> list:
    return [name for name, lvl in _load_maturity().items() if lvl == level]
