"""Endorsement tracking for snapshots."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _endorsements_path() -> Path:
    return get_stash_dir() / "endorsements.json"


def _load_endorsements() -> dict:
    p = _endorsements_path()
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_endorsements(data: dict) -> None:
    p = _endorsements_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def add_endorsement(name: str, endorser: str) -> bool:
    """Add an endorser to a snapshot. Returns False if already endorsed."""
    data = _load_endorsements()
    endorsers = data.get(name, [])
    if endorser in endorsers:
        return False
    endorsers.append(endorser)
    data[name] = endorsers
    _save_endorsements(data)
    return True


def remove_endorsement(name: str, endorser: str) -> bool:
    """Remove an endorser from a snapshot. Returns False if not found."""
    data = _load_endorsements()
    endorsers = data.get(name, [])
    if endorser not in endorsers:
        return False
    endorsers.remove(endorser)
    data[name] = endorsers
    _save_endorsements(data)
    return True


def get_endorsements(name: str) -> list:
    """Return list of endorsers for a snapshot."""
    data = _load_endorsements()
    return data.get(name, [])


def endorsement_count(name: str) -> int:
    return len(get_endorsements(name))


def clear_endorsements(name: str) -> bool:
    """Remove all endorsements for a snapshot."""
    data = _load_endorsements()
    if name not in data:
        return False
    del data[name]
    _save_endorsements(data)
    return True


def top_endorsed(n: int = 5) -> list:
    """Return top n snapshots by endorsement count."""
    data = _load_endorsements()
    ranked = sorted(data.items(), key=lambda x: len(x[1]), reverse=True)
    return [(name, len(endorsers)) for name, endorsers in ranked[:n]]
