"""Lifecycle state tracking for snapshots (draft, active, deprecated, retired)."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir

LIFECYCLE_STATES = {"draft", "active", "deprecated", "retired"}
DEFAULT_STATE = "active"


def _lifecycle_path() -> Path:
    return get_stash_dir() / "lifecycle.json"


def _load_lifecycle() -> dict:
    p = _lifecycle_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_lifecycle(data: dict) -> None:
    _lifecycle_path().write_text(json.dumps(data, indent=2))


def set_lifecycle(name: str, state: str) -> bool:
    """Set lifecycle state for a snapshot. Returns False if state is invalid."""
    if state not in LIFECYCLE_STATES:
        return False
    data = _load_lifecycle()
    data[name] = state
    _save_lifecycle(data)
    return True


def get_lifecycle(name: str, default: str = DEFAULT_STATE) -> str:
    """Get lifecycle state for a snapshot."""
    return _load_lifecycle().get(name, default)


def remove_lifecycle(name: str) -> bool:
    """Remove lifecycle entry. Returns False if not found."""
    data = _load_lifecycle()
    if name not in data:
        return False
    del data[name]
    _save_lifecycle(data)
    return True


def list_by_state(state: str) -> list[str]:
    """Return all snapshot names with the given lifecycle state."""
    data = _load_lifecycle()
    return [name for name, s in data.items() if s == state]


def lifecycle_summary() -> dict[str, list[str]]:
    """Return a dict mapping each state to its snapshot names."""
    data = _load_lifecycle()
    summary: dict[str, list[str]] = {s: [] for s in LIFECYCLE_STATES}
    for name, state in data.items():
        if state in summary:
            summary[state].append(name)
    return summary
