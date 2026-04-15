"""CLI commands for the audit trail feature."""

from __future__ import annotations

import argparse
from typing import Optional

from stashrun.snapshots_audit import clear_audit_log, get_audit_log


def cmd_audit_log(args: argparse.Namespace) -> None:
    """Show audit log, optionally filtered."""
    entries = get_audit_log(
        snapshot_name=getattr(args, "name", None),
        action=getattr(args, "action", None),
        limit=getattr(args, "limit", None),
    )
    if not entries:
        print("No audit entries found.")
        return
    for e in entries:
        detail = f" ({e['detail']})" if e.get("detail") else ""
        print(f"[{e['timestamp']}] {e['action']:10s} {e['snapshot']:30s} user={e['user']}{detail}")


def cmd_audit_clear(args: argparse.Namespace) -> None:
    """Clear audit log entries."""
    name: Optional[str] = getattr(args, "name", None)
    removed = clear_audit_log(snapshot_name=name)
    if name:
        print(f"Removed {removed} audit entries for snapshot '{name}'.")
    else:
        print(f"Cleared {removed} audit entries.")


def register_audit_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # audit-log
    p_log = subparsers.add_parser("audit-log", help="Show the audit trail")
    p_log.add_argument("--name", help="Filter by snapshot name")
    p_log.add_argument("--action", help="Filter by action (e.g. save, restore, delete)")
    p_log.add_argument("--limit", type=int, help="Show only the last N entries")
    p_log.set_defaults(func=cmd_audit_log)

    # audit-clear
    p_clear = subparsers.add_parser("audit-clear", help="Clear audit log entries")
    p_clear.add_argument("--name", help="Clear only entries for this snapshot")
    p_clear.set_defaults(func=cmd_audit_clear)
