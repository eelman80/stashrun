"""CLI commands for snapshot alias management."""

from __future__ import annotations

import argparse

from stashrun.aliases import (
    list_aliases,
    remove_alias,
    rename_alias,
    resolve_alias,
    set_alias,
)


def cmd_alias_set(args: argparse.Namespace) -> None:
    set_alias(args.alias, args.snapshot)
    print(f"Alias '{args.alias}' -> '{args.snapshot}' saved.")


def cmd_alias_remove(args: argparse.Namespace) -> None:
    if remove_alias(args.alias):
        print(f"Alias '{args.alias}' removed.")
    else:
        print(f"Alias '{args.alias}' not found.")


def cmd_alias_resolve(args: argparse.Namespace) -> None:
    target = resolve_alias(args.alias)
    if target:
        print(target)
    else:
        print(f"No alias named '{args.alias}'.")


def cmd_alias_list(args: argparse.Namespace) -> None:  # noqa: ARG001
    aliases = list_aliases()
    if not aliases:
        print("No aliases defined.")
        return
    for alias, snapshot in sorted(aliases.items()):
        print(f"  {alias} -> {snapshot}")


def cmd_alias_rename(args: argparse.Namespace) -> None:
    if rename_alias(args.old, args.new):
        print(f"Alias '{args.old}' renamed to '{args.new}'.")
    else:
        print(f"Alias '{args.old}' not found.")


def register_alias_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("alias", help="Manage snapshot aliases")
    sub = p.add_subparsers(dest="alias_cmd", required=True)

    s = sub.add_parser("set", help="Create or update an alias")
    s.add_argument("alias")
    s.add_argument("snapshot")
    s.set_defaults(func=cmd_alias_set)

    r = sub.add_parser("remove", help="Delete an alias")
    r.add_argument("alias")
    r.set_defaults(func=cmd_alias_remove)

    v = sub.add_parser("resolve", help="Print the snapshot an alias points to")
    v.add_argument("alias")
    v.set_defaults(func=cmd_alias_resolve)

    sub.add_parser("list", help="List all aliases").set_defaults(func=cmd_alias_list)

    rn = sub.add_parser("rename", help="Rename an alias")
    rn.add_argument("old")
    rn.add_argument("new")
    rn.set_defaults(func=cmd_alias_rename)
