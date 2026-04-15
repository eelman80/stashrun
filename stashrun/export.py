"""Export and import snapshots to/from portable file formats."""

import json
import os
from pathlib import Path
from typing import Optional

from stashrun.storage import load_snapshot, save_snapshot


def export_snapshot(name: str, output_path: str, fmt: str = "json") -> bool:
    """Export a named snapshot to a file.

    Args:
        name: Snapshot name to export.
        output_path: Destination file path.
        fmt: Export format, either 'json' or 'dotenv'.

    Returns:
        True if export succeeded, False if snapshot not found.
    """
    data = load_snapshot(name)
    if data is None:
        return False

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "dotenv":
        lines = []
        for key, value in sorted(data.items()):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    return True


def import_snapshot(name: str, input_path: str, fmt: str = "json") -> bool:
    """Import a snapshot from a file.

    Args:
        name: Snapshot name to save as.
        input_path: Source file path.
        fmt: Import format, either 'json' or 'dotenv'.

    Returns:
        True if import succeeded, False if file not found or parse error.
    """
    path = Path(input_path)
    if not path.exists():
        return False

    try:
        content = path.read_text(encoding="utf-8")
        if fmt == "dotenv":
            data = _parse_dotenv(content)
        else:
            data = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return False

    save_snapshot(name, data)
    return True


def _parse_dotenv(content: str) -> dict:
    """Parse a .env file into a key/value dict."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        value = raw_value.strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        result[key] = value
    return result
