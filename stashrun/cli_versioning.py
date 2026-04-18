"""CLI commands for snapshot versioning."""

import argparse

from stashrun.snapshots_versioning import (
    push_version,
    list_versions,
    get_version,
    restore_version,
    drop_versions,
    version_count,
)


def cmd_version_push(args: argparse.Namespace) -> None:
    n = push_version(args.name)
    if n is None:
        print(f"Snapshot '{args.name}' not found.")
    else:
        print(f"Pushed version {n} for '{args.name}'.")


def cmd_version_list(args: argparse.Namespace) -> None:
    versions = list_versions(args.name)
    if not versions:
        print(f"No versions stored for '{args.name}'.")
        return
    for i, env in enumerate(versions, 1):
        print(f"  v{i}: {len(env)} key(s)")


def cmd_version_show(args: argparse.Namespace) -> None:
    env = get_version(args.name, args.index)
    if env is None:
        print(f"Version {args.index} not found for '{args.name}'.")
        return
    for k, v in env.items():
        print(f"  {k}={v}")


def cmd_version_restore(args: argparse.Namespace) -> None:
    ok = restore_version(args.name, args.index)
    if ok:
        print(f"Restored '{args.name}' to version {args.index}.")
    else:
        print(f"Version {args.index} not found for '{args.name}'.")


def cmd_version_drop(args: argparse.Namespace) -> None:
    ok = drop_versions(args.name)
    if ok:
        print(f"Dropped all versions for '{args.name}'.")
    else:
        print(f"No versions found for '{args.name}'.")


def register_versioning_commands(subparsers) -> None:
    p = subparsers.add_parser("version-push", help="Push current snapshot as a new version")
    p.add_argument("name")
    p.set_defaults(func=cmd_version_push)

    p = subparsers.add_parser("version-list", help="List stored versions of a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_version_list)

    p = subparsers.add_parser("version-show", help="Show a specific version")
    p.add_argument("name")
    p.add_argument("index", type=int)
    p.set_defaults(func=cmd_version_show)

    p = subparsers.add_parser("version-restore", help="Restore snapshot to a specific version")
    p.add_argument("name")
    p.add_argument("index", type=int)
    p.set_defaults(func=cmd_version_restore)

    p = subparsers.add_parser("version-drop", help="Drop all versions for a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_version_drop)
