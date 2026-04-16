"""Validation utilities for snapshots — check required keys, value patterns, etc."""

import re
from typing import Optional
from stashrun.snapshot import get_snapshot


def validate_required_keys(env: dict, required: list[str]) -> list[str]:
    """Return list of required keys missing from env."""
    return [k for k in required if k not in env]


def validate_key_pattern(env: dict, pattern: str) -> dict[str, bool]:
    """Check each key against a regex pattern. Returns {key: matches}."""
    compiled = re.compile(pattern)
    return {k: bool(compiled.fullmatch(k)) for k in env}


def validate_value_nonempty(env: dict) -> list[str]:
    """Return list of keys whose values are empty strings."""
    return [k for k, v in env.items() if v == ""]


def validate_value_pattern(env: dict, key: str, pattern: str) -> Optional[bool]:
    """Check if a specific key's value matches a regex. Returns None if key missing."""
    if key not in env:
        return None
    return bool(re.fullmatch(pattern, env[key]))


def validate_snapshot(
    name: str,
    required_keys: Optional[list[str]] = None,
    key_pattern: Optional[str] = None,
    no_empty_values: bool = False,
) -> dict:
    """
    Run all requested validations against a named snapshot.
    Returns a report dict with keys: 'found', 'missing_keys', 'invalid_keys', 'empty_values'.
    """
    env = get_snapshot(name)
    if env is None:
        return {"found": False}

    report: dict = {"found": True, "missing_keys": [], "invalid_keys": [], "empty_values": []}

    if required_keys:
        report["missing_keys"] = validate_required_keys(env, required_keys)

    if key_pattern:
        results = validate_key_pattern(env, key_pattern)
        report["invalid_keys"] = [k for k, ok in results.items() if not ok]

    if no_empty_values:
        report["empty_values"] = validate_value_nonempty(env)

    report["valid"] = not any([
        report["missing_keys"],
        report["invalid_keys"],
        report["empty_values"],
    ])
    return report
