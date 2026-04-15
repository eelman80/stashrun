"""CLI commands for profile management."""

from __future__ import annotations

import argparse

from stashrun.profiles import (
    add_snapshot_to_profile,
    create_profile,
    delete_profile,
    get_profile,
    list_profiles,
    remove_snapshot_from_profile,
)


def cmd_profile_create(args: argparse.Namespace) -> None:
    if create_profile(args.name):
        print(f"Profile '{args.name}' created.")
    else:
        print(f"Profile '{args.name}' already exists.")


def cmd_profile_delete(args: argparse.Namespace) -> None:
    if delete_profile(args.name):
        print(f"Profile '{args.name}' deleted.")
    else:
        print(f"Profile '{args.name}' not found.")


def cmd_profile_add(args: argparse.Namespace) -> None:
    if add_snapshot_to_profile(args.profile, args.snapshot):
        print(f"Snapshot '{args.snapshot}' added to profile '{args.profile}'.")
    else:
        print(f"Snapshot '{args.snapshot}' already in profile '{args.profile}'.")


def cmd_profile_remove(args: argparse.Namespace) -> None:
    if remove_snapshot_from_profile(args.profile, args.snapshot):
        print(f"Snapshot '{args.snapshot}' removed from profile '{args.profile}'.")
    else:
        print(f"Snapshot '{args.snapshot}' not found in profile '{args.profile}'.")


def cmd_profile_show(args: argparse.Namespace) -> None:
    snapshots = get_profile(args.name)
    if snapshots is None:
        print(f"Profile '{args.name}' not found.")
        return
    if not snapshots:
        print(f"Profile '{args.name}' is empty.")
        return
    for s in snapshots:
        print(s)


def cmd_profile_list(args: argparse.Namespace) -> None:
    profiles = list_profiles()
    if not profiles:
        print("No profiles found.")
        return
    for p in profiles:
        print(p)


def register_profile_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("profile", help="Manage snapshot profiles")
    sub = p.add_subparsers(dest="profile_cmd", required=True)

    pc = sub.add_parser("create", help="Create a new profile")
    pc.add_argument("name")
    pc.set_defaults(func=cmd_profile_create)

    pd = sub.add_parser("delete", help="Delete a profile")
    pd.add_argument("name")
    pd.set_defaults(func=cmd_profile_delete)

    pa = sub.add_parser("add", help="Add snapshot to profile")
    pa.add_argument("profile")
    pa.add_argument("snapshot")
    pa.set_defaults(func=cmd_profile_add)

    pr = sub.add_parser("remove", help="Remove snapshot from profile")
    pr.add_argument("profile")
    pr.add_argument("snapshot")
    pr.set_defaults(func=cmd_profile_remove)

    ps = sub.add_parser("show", help="Show snapshots in a profile")
    ps.add_argument("name")
    ps.set_defaults(func=cmd_profile_show)

    pl = sub.add_parser("list", help="List all profiles")
    pl.set_defaults(func=cmd_profile_list)
