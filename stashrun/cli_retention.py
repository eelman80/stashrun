"""CLI commands for snapshot retention policies."""
from __future__ import annotations

import argparse

from stashrun.snapshots_retention import (
    set_retention,
    get_retention,
    remove_retention,
    list_retention,
    apply_retention,
    _VALID_POLICIES,
)


def cmd_retention_set(args: argparse.Namespace) -> None:
    ok = set_retention(args.name, args.policy, args.value)
    if not ok:
        print(f"Invalid policy '{args.policy}'. Choose from: {', '.join(sorted(_VALID_POLICIES))}")
    else:
        print(f"Retention policy '{args.policy}' (value={args.value}) set for '{args.name}'.")


def cmd_retention_get(args: argparse.Namespace) -> None:
    entry = get_retention(args.name)
    if entry is None:
        print(f"No retention policy set for '{args.name}'.")
    else:
        print(f"{args.name}: policy={entry['policy']}, value={entry.get('value', 0)}")


def cmd_retention_remove(args: argparse.Namespace) -> None:
    ok = remove_retention(args.name)
    if ok:
        print(f"Retention policy removed for '{args.name}'.")
    else:
        print(f"No retention policy found for '{args.name}'.")


def cmd_retention_list(args: argparse.Namespace) -> None:
    data = list_retention()
    if not data:
        print("No retention policies configured.")
        return
    for name, entry in sorted(data.items()):
        print(f"  {name}: policy={entry['policy']}, value={entry.get('value', 0)}")


def cmd_retention_apply(args: argparse.Namespace) -> None:
    removed = apply_retention(args.name)
    if not removed:
        print(f"Nothing to prune for '{args.name}'.")
    else:
        print(f"Pruned {len(removed)} snapshot(s): {', '.join(removed)}")


def register_retention_commands(subparsers) -> None:
    p = subparsers.add_parser("retention-set", help="Set a retention policy for a snapshot")
    p.add_argument("name")
    p.add_argument("policy", choices=sorted(_VALID_POLICIES))
    p.add_argument("--value", type=int, default=0, help="Numeric parameter for policy")
    p.set_defaults(func=cmd_retention_set)

    p = subparsers.add_parser("retention-get", help="Show retention policy for a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_retention_get)

    p = subparsers.add_parser("retention-remove", help="Remove retention policy for a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_retention_remove)

    p = subparsers.add_parser("retention-list", help="List all retention policies")
    p.set_defaults(func=cmd_retention_list)

    p = subparsers.add_parser("retention-apply", help="Apply retention policy and prune old snapshots")
    p.add_argument("name")
    p.set_defaults(func=cmd_retention_apply)
