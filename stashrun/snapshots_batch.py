"""Batch operations on multiple snapshots."""

from typing import List, Dict, Optional, Tuple
from stashrun.snapshot import get_snapshot, remove_snapshot, list_all_snapshots
from stashrun.snapshots_copy import copy_snapshot
from stashrun.tags import get_snapshots_by_tag


def batch_delete(names: List[str]) -> Dict[str, bool]:
    """Delete multiple snapshots. Returns {name: success}."""
    results = {}
    for name in names:
        try:
            results[name] = remove_snapshot(name)
        except Exception:
            results[name] = False
    return results


def batch_copy(pairs: List[Tuple[str, str]], overwrite: bool = False) -> Dict[str, bool]:
    """Copy multiple snapshots. pairs is list of (src, dst)."""
    results = {}
    for src, dst in pairs:
        try:
            results[f"{src}->{dst}"] = copy_snapshot(src, dst, overwrite=overwrite)
        except Exception:
            results[f"{src}->{dst}"] = False
    return results


def batch_tag_delete(tag: str) -> Dict[str, bool]:
    """Delete all snapshots with a given tag."""
    names = get_snapshots_by_tag(tag)
    return batch_delete(names)


def batch_export_names(pattern: Optional[str] = None) -> List[str]:
    """List snapshot names optionally filtered by substring pattern."""
    all_names = list_all_snapshots()
    if pattern:
        return [n for n in all_names if pattern.lower() in n.lower()]
    return all_names


def batch_get(names: List[str]) -> Dict[str, Optional[dict]]:
    """Fetch env dicts for multiple snapshots."""
    return {name: get_snapshot(name) for name in names}
