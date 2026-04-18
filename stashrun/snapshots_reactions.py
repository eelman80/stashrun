"""Emoji reactions for snapshots."""
import json
from pathlib import Path
from stashrun.storage import get_stash_dir

VALID_REACTIONS = {"👍", "👎", "❤️", "🔥", "⚠️", "✅", "🚀", "🐛"}


def _reactions_path() -> Path:
    return get_stash_dir() / "reactions.json"


def _load_reactions() -> dict:
    p = _reactions_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_reactions(data: dict) -> None:
    _reactions_path().write_text(json.dumps(data, indent=2))


def add_reaction(name: str, reaction: str) -> bool:
    if reaction not in VALID_REACTIONS:
        return False
    data = _load_reactions()
    entry = data.setdefault(name, [])
    if reaction not in entry:
        entry.append(reaction)
        _save_reactions(data)
    return True


def remove_reaction(name: str, reaction: str) -> bool:
    data = _load_reactions()
    entry = data.get(name, [])
    if reaction not in entry:
        return False
    entry.remove(reaction)
    if not entry:
        del data[name]
    else:
        data[name] = entry
    _save_reactions(data)
    return True


def get_reactions(name: str) -> list:
    return _load_reactions().get(name, [])


def clear_reactions(name: str) -> bool:
    data = _load_reactions()
    if name not in data:
        return False
    del data[name]
    _save_reactions(data)
    return True


def list_all_reactions() -> dict:
    return _load_reactions()
