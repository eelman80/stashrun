"""Template support for stashrun: save and apply env variable templates."""

import json
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir


def _templates_path() -> Path:
    return get_stash_dir() / "templates.json"


def _load_templates() -> dict:
    path = _templates_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_templates(data: dict) -> None:
    path = _templates_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_template(name: str, variables: dict) -> bool:
    """Save a named template with a set of env variable keys and optional default values."""
    templates = _load_templates()
    templates[name] = variables
    _save_templates(templates)
    return True


def get_template(name: str) -> Optional[dict]:
    """Return the template dict or None if not found."""
    return _load_templates().get(name)


def delete_template(name: str) -> bool:
    """Remove a template by name. Returns False if not found."""
    templates = _load_templates()
    if name not in templates:
        return False
    del templates[name]
    _save_templates(templates)
    return True


def list_templates() -> list[str]:
    """Return sorted list of all template names."""
    return sorted(_load_templates().keys())


def apply_template(name: str, env: dict) -> Optional[dict]:
    """Filter env dict to only keys defined in the template, using template defaults for missing keys."""
    template = get_template(name)
    if template is None:
        return None
    result = {}
    for key, default in template.items():
        if key in env:
            result[key] = env[key]
        elif default is not None:
            result[key] = default
    return result
