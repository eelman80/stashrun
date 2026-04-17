"""Group multiple snapshots under a named collection."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _groups_path() -> Path:
    return get_stash_dir() / "groups.json"


def _load_groups() -> dict:
    p = _groups_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_groups(data: dict) -> None:
    _groups_path().write_text(json.dumps(data, indent=2))


def create_group(name: str) -> bool:
    groups = _load_groups()
    if name in groups:
        return False
    groups[name] = []
    _save_groups(groups)
    return True


def delete_group(name: str) -> bool:
    groups = _load_groups()
    if name not in groups:
        return False
    del groups[name]
    _save_groups(groups)
    return True


def add_to_group(group: str, snapshot: str) -> bool:
    groups = _load_groups()
    if group not in groups:
        return False
    if snapshot not in groups[group]:
        groups[group].append(snapshot)
        _save_groups(groups)
    return True


def remove_from_group(group: str, snapshot: str) -> bool:
    groups = _load_groups()
    if group not in groups or snapshot not in groups[group]:
        return False
    groups[group].remove(snapshot)
    _save_groups(groups)
    return True


def get_group(name: str) -> list | None:
    return _load_groups().get(name)


def list_groups() -> list[str]:
    return list(_load_groups().keys())


def find_groups_for_snapshot(snapshot: str) -> list[str]:
    return [g for g, members in _load_groups().items() if snapshot in members]
