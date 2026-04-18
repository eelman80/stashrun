"""Track dependencies between snapshots (e.g. snapshot B requires snapshot A)."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _deps_path() -> Path:
    return get_stash_dir() / "dependencies.json"


def _load_deps() -> dict:
    p = _deps_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_deps(data: dict) -> None:
    _deps_path().write_text(json.dumps(data, indent=2))


def add_dependency(name: str, requires: str) -> bool:
    """Record that snapshot `name` depends on snapshot `requires`."""
    if name == requires:
        return False
    data = _load_deps()
    deps = data.setdefault(name, [])
    if requires in deps:
        return False
    deps.append(requires)
    _save_deps(data)
    return True


def remove_dependency(name: str, requires: str) -> bool:
    data = _load_deps()
    deps = data.get(name, [])
    if requires not in deps:
        return False
    deps.remove(requires)
    if not deps:
        del data[name]
    else:
        data[name] = deps
    _save_deps(data)
    return True


def get_dependencies(name: str) -> list:
    """Return direct dependencies of a snapshot."""
    return _load_deps().get(name, [])


def get_dependents(name: str) -> list:
    """Return snapshots that depend on `name`."""
    return [k for k, v in _load_deps().items() if name in v]


def clear_dependencies(name: str) -> bool:
    data = _load_deps()
    if name not in data:
        return False
    del data[name]
    _save_deps(data)
    return True


def all_dependencies() -> dict:
    return _load_deps()
