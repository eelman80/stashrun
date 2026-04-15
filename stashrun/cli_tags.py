"""CLI commands for snapshot tagging."""

from __future__ import annotations

import argparse

from stashrun import tags as tag_mod


def cmd_tag_add(args: argparse.Namespace) -> int:
    added = tag_mod.add_tag(args.snapshot, args.tag)
    if added:
        print(f"Tag '{args.tag}' added to snapshot '{args.snapshot}'.")
    else:
        print(f"Tag '{args.tag}' already present on '{args.snapshot}'.")
    return 0


def cmd_tag_remove(args: argparse.Namespace) -> int:
    removed = tag_mod.remove_tag(args.snapshot, args.tag)
    if removed:
        print(f"Tag '{args.tag}' removed from snapshot '{args.snapshot}'.")
    else:
        print(f"Tag '{args.tag}' not found on snapshot '{args.snapshot}'.")
        return 1
    return 0


def cmd_tag_list(args: argparse.Namespace) -> int:
    tags = tag_mod.get_tags(args.snapshot)
    if not tags:
        print(f"No tags for snapshot '{args.snapshot}'.")
    else:
        for t in tags:
            print(t)
    return 0


def cmd_tag_find(args: argparse.Namespace) -> int:
    snapshots = tag_mod.find_by_tag(args.tag)
    if not snapshots:
        print(f"No snapshots tagged '{args.tag}'.")
    else:
        for s in snapshots:
            print(s)
    return 0


def register_tag_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    tag_parser = subparsers.add_parser("tag", help="Manage snapshot tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd", required=True)

    p_add = tag_sub.add_parser("add", help="Add a tag to a snapshot")
    p_add.add_argument("snapshot", help="Snapshot name")
    p_add.add_argument("tag", help="Tag to add")
    p_add.set_defaults(func=cmd_tag_add)

    p_rm = tag_sub.add_parser("remove", help="Remove a tag from a snapshot")
    p_rm.add_argument("snapshot", help="Snapshot name")
    p_rm.add_argument("tag", help="Tag to remove")
    p_rm.set_defaults(func=cmd_tag_remove)

    p_ls = tag_sub.add_parser("list", help="List tags for a snapshot")
    p_ls.add_argument("snapshot", help="Snapshot name")
    p_ls.set_defaults(func=cmd_tag_list)

    p_find = tag_sub.add_parser("find", help="Find snapshots by tag")
    p_find.add_argument("tag", help="Tag to search for")
    p_find.set_defaults(func=cmd_tag_find)
