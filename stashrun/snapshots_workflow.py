"""Workflow support: named sequences of snapshots to restore in order."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
from stashrun.storage import get_stash_dir
from stashrun.snapshot import get_snapshot, restore_snapshot


def _workflows_path() -> Path:
    return get_stash_dir() / "workflows.json"


def _load_workflows() -> dict:
    p = _workflows_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_workflows(data: dict) -> None:
    _workflows_path().write_text(json.dumps(data, indent=2))


def create_workflow(name: str, steps: list[str]) -> bool:
    data = _load_workflows()
    if name in data:
        return False
    data[name] = {"steps": steps}
    _save_workflows(data)
    return True


def delete_workflow(name: str) -> bool:
    data = _load_workflows()
    if name not in data:
        return False
    del data[name]
    _save_workflows(data)
    return True


def get_workflow(name: str) -> Optional[dict]:
    return _load_workflows().get(name)


def list_workflows() -> list[str]:
    return list(_load_workflows().keys())


def add_step(workflow: str, snapshot_name: str) -> bool:
    data = _load_workflows()
    if workflow not in data:
        return False
    data[workflow]["steps"].append(snapshot_name)
    _save_workflows(data)
    return True


def remove_step(workflow: str, index: int) -> bool:
    data = _load_workflows()
    if workflow not in data:
        return False
    steps = data[workflow]["steps"]
    if index < 0 or index >= len(steps):
        return False
    steps.pop(index)
    _save_workflows(data)
    return True


def run_workflow(name: str) -> tuple[int, list[str]]:
    """Run all steps; returns (applied_count, missing_names)."""
    wf = get_workflow(name)
    if wf is None:
        return 0, []
    applied, missing = 0, []
    for step in wf["steps"]:
        if get_snapshot(step) is None:
            missing.append(step)
        else:
            restore_snapshot(step)
            applied += 1
    return applied, missing
