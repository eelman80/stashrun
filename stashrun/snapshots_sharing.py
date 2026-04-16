"""Snapshot sharing: encode/decode snapshots as portable share strings."""

import base64
import json
from typing import Optional

from stashrun.snapshot import get_snapshot, create_snapshot


def encode_snapshot(name: str) -> Optional[str]:
    """Encode a snapshot's env dict as a base64 share string."""
    env = get_snapshot(name)
    if env is None:
        return None
    payload = json.dumps({"name": name, "env": env}, separators=(",", ":"))
    return base64.urlsafe_b64encode(payload.encode()).decode()


def decode_share_string(share_str: str) -> Optional[dict]:
    """Decode a share string into {name, env}. Returns None on failure."""
    try:
        payload = base64.urlsafe_b64decode(share_str.encode()).decode()
        data = json.loads(payload)
        if "name" in data and "env" in data:
            return data
        return None
    except Exception:
        return None


def import_share_string(share_str: str, name: Optional[str] = None) -> Optional[str]:
    """Import a share string as a new snapshot. Returns snapshot name or None."""
    data = decode_share_string(share_str)
    if data is None:
        return None
    target_name = name or data["name"]
    create_snapshot(target_name, env=data["env"])
    return target_name


def share_summary(share_str: str) -> Optional[dict]:
    """Return a summary dict (name, key_count) for a share string."""
    data = decode_share_string(share_str)
    if data is None:
        return None
    return {"name": data["name"], "key_count": len(data["env"])}
