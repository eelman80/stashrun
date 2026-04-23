"""Attribution tracking for snapshots — who created, modified, or contributed."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashrun.storage import get_stash_dir


def _attribution_path() -> Path:
    return get_stash_dir() / "attributions.json"


def _load_attribution() -> Dict[str, Dict]:
    p = _attribution_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_attribution(data: Dict[str, Dict]) -> None:
    _attribution_path().write_text(json.dumps(data, indent=2))


def set_attribution(name: str, author: str, contributors: Optional[List[str]] = None, source: Optional[str] = None) -> None:
    """Set attribution metadata for a snapshot."""
    data = _load_attribution()
    data[name] = {
        "author": author,
        "contributors": list(set(contributors or [])),
        "source": source,
    }
    _save_attribution(data)


def get_attribution(name: str) -> Optional[Dict]:
    """Return attribution info for a snapshot, or None if not set."""
    return _load_attribution().get(name)


def add_contributor(name: str, contributor: str) -> bool:
    """Add a contributor to an existing attribution entry. Returns False if not found."""
    data = _load_attribution()
    if name not in data:
        return False
    contributors = data[name].get("contributors", [])
    if contributor not in contributors:
        contributors.append(contributor)
        data[name]["contributors"] = contributors
        _save_attribution(data)
    return True


def remove_attribution(name: str) -> bool:
    """Remove attribution for a snapshot. Returns False if not found."""
    data = _load_attribution()
    if name not in data:
        return False
    del data[name]
    _save_attribution(data)
    return True


def list_attributions() -> Dict[str, Dict]:
    """Return all attribution entries."""
    return _load_attribution()


def find_by_author(author: str) -> List[str]:
    """Return snapshot names attributed to a given author."""
    return [n for n, v in _load_attribution().items() if v.get("author") == author]
