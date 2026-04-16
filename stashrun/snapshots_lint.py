"""Lint snapshots for common issues and style problems."""

from typing import Optional
from stashrun.snapshot import get_snapshot


LINT_RULES = [
    "no_empty_values",
    "no_whitespace_keys",
    "no_lowercase_keys",
    "no_duplicate_prefixes",
    "no_very_long_values",
]

MAX_VALUE_LENGTH = 1024


def lint_no_empty_values(env: dict) -> list[str]:
    return [f"Key '{k}' has an empty value." for k, v in env.items() if v == ""]


def lint_no_whitespace_keys(env: dict) -> list[str]:
    return [f"Key '{k}' contains whitespace." for k in env if any(c.isspace() for c in k)]


def lint_no_lowercase_keys(env: dict) -> list[str]:
    return [f"Key '{k}' is not uppercase (convention)." for k in env if k != k.upper()]


def lint_no_duplicate_prefixes(env: dict) -> list[str]:
    from collections import Counter
    prefixes = [k.split("_")[0] for k in env if "_" in k]
    counts = Counter(prefixes)
    warnings = []
    seen = set()
    for k in env:
        prefix = k.split("_")[0] if "_" in k else None
        if prefix and counts[prefix] == 1 and prefix not in seen:
            seen.add(prefix)
    return warnings


def lint_no_very_long_values(env: dict) -> list[str]:
    return [
        f"Key '{k}' has a very long value ({len(v)} chars)."
        for k, v in env.items()
        if len(v) > MAX_VALUE_LENGTH
    ]


_RULE_FNS = {
    "no_empty_values": lint_no_empty_values,
    "no_whitespace_keys": lint_no_whitespace_keys,
    "no_lowercase_keys": lint_no_lowercase_keys,
    "no_duplicate_prefixes": lint_no_duplicate_prefixes,
    "no_very_long_values": lint_no_very_long_values,
}


def lint_snapshot(
    name: str,
    rules: Optional[list[str]] = None,
) -> dict:
    """Run lint rules against a snapshot. Returns {passed, warnings, missing}."""
    env = get_snapshot(name)
    if env is None:
        return {"passed": False, "warnings": [], "missing": True}

    active_rules = rules if rules is not None else LINT_RULES
    warnings = []
    for rule in active_rules:
        fn = _RULE_FNS.get(rule)
        if fn:
            warnings.extend(fn(env))

    return {"passed": len(warnings) == 0, "warnings": warnings, "missing": False}
