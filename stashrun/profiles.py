"""Profile management: named collections of snapshots for a project context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashrun.storage import get_stash_dir


def _profiles_path() -> Path:
    return get_stash_dir() / "profiles.json"


def _load_profiles() -> Dict[str, List[str]]:
    path = _profiles_path()
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_profiles(profiles: Dict[str, List[str]]) -> None:
    path = _profiles_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(profiles, fh, indent=2)


def create_profile(name: str) -> bool:
    """Create a new empty profile. Returns False if it already exists."""
    profiles = _load_profiles()
    if name in profiles:
        return False
    profiles[name] = []
    _save_profiles(profiles)
    return True


def delete_profile(name: str) -> bool:
    """Delete a profile by name. Returns False if not found."""
    profiles = _load_profiles()
    if name not in profiles:
        return False
    del profiles[name]
    _save_profiles(profiles)
    return True


def add_snapshot_to_profile(profile: str, snapshot_name: str) -> bool:
    """Add a snapshot name to a profile. Creates profile if missing."""
    profiles = _load_profiles()
    if profile not in profiles:
        profiles[profile] = []
    if snapshot_name in profiles[profile]:
        return False
    profiles[profile].append(snapshot_name)
    _save_profiles(profiles)
    return True


def remove_snapshot_from_profile(profile: str, snapshot_name: str) -> bool:
    """Remove a snapshot from a profile. Returns False if not found."""
    profiles = _load_profiles()
    if profile not in profiles or snapshot_name not in profiles[profile]:
        return False
    profiles[profile].remove(snapshot_name)
    _save_profiles(profiles)
    return True


def get_profile(name: str) -> Optional[List[str]]:
    """Return list of snapshot names in a profile, or None if missing."""
    return _load_profiles().get(name)


def list_profiles() -> List[str]:
    """Return all profile names."""
    return list(_load_profiles().keys())
