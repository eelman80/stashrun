"""Snapshot relations: link snapshots as related/derived/conflicting."""
from __future__ import annotations
import json
from pathlib import Path
from stashrun.storage import get_stash_dir

RELATION_TYPES = {"related", "derived", "conflicting", "supersedes"}


def _relations_path() -> Path:
    return get_stash_dir() / "relations.json"


def _load_relations() -> dict:
    p = _relations_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_relations(data: dict) -> None:
    _relations_path().write_text(json.dumps(data, indent=2))


def add_relation(source: str, target: str, relation: str) -> bool:
    if relation not in RELATION_TYPES:
        return False
    if source == target:
        return False
    data = _load_relations()
    entry = data.setdefault(source, {})
    targets = entry.setdefault(relation, [])
    if target in targets:
        return False
    targets.append(target)
    _save_relations(data)
    return True


def remove_relation(source: str, target: str, relation: str) -> bool:
    data = _load_relations()
    targets = data.get(source, {}).get(relation, [])
    if target not in targets:
        return False
    targets.remove(target)
    _save_relations(data)
    return True


def get_relations(name: str) -> dict:
    return _load_relations().get(name, {})


def find_related(name: str, relation: str) -> list:
    return _load_relations().get(name, {}).get(relation, [])


def clear_relations(name: str) -> bool:
    data = _load_relations()
    if name not in data:
        return False
    del data[name]
    _save_relations(data)
    return True
