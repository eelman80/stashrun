"""CLI entry point for stashrun."""

import sys
import json
import argparse

from stashrun.snapshot import (
    create_snapshot,
    restore_snapshot,
    get_snapshot,
    remove_snapshot,
    list_all_snapshots,
)
from stashrun.env import diff_env, capture_env


def cmd_save(args: argparse.Namespace) -> int:
    prefixes = args.prefix or None
    keys = args.key or None
    env = create_snapshot(args.name, keys=keys, prefixes=prefixes)
    print(f"Saved snapshot '{args.name}' with {len(env)} variable(s).")
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    env = restore_snapshot(args.name, overwrite=not args.no_overwrite)
    if env is None:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        return 1
    print(f"Restored snapshot '{args.name}' ({len(env)} variable(s)).")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    snapshots = list_all_snapshots()
    if not snapshots:
        print("No snapshots found.")
    else:
        for name in snapshots:
            print(name)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    env = get_snapshot(args.name)
    if env is None:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        return 1
    print(json.dumps(env, indent=2, sort_keys=True))
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    if remove_snapshot(args.name):
        print(f"Deleted snapshot '{args.name}'.")
        return 0
    print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
    return 1


def cmd_diff(args: argparse.Namespace) -> int:
    base = get_snapshot(args.base)
    if base is None:
        print(f"Error: snapshot '{args.base}' not found.", file=sys.stderr)
        return 1
    target = get_snapshot(args.target) if args.target else capture_env()
    result = diff_env(base, target)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stashrun",
        description="Snapshot and restore environment variables.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="Save current env as a snapshot.")
    p_save.add_argument("name", help="Snapshot name.")
    p_save.add_argument("--key", action="append", metavar="KEY")
    p_save.add_argument("--prefix", action="append", metavar="PREFIX")
    p_save.set_defaults(func=cmd_save)

    p_restore = sub.add_parser("restore", help="Restore a snapshot.")
    p_restore.add_argument("name", help="Snapshot name.")
    p_restore.add_argument("--no-overwrite", action="store_true")
    p_restore.set_defaults(func=cmd_restore)

    p_list = sub.add_parser("list", help="List all snapshots.")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Show snapshot contents.")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_show)

    p_del = sub.add_parser("delete", help="Delete a snapshot.")
    p_del.add_argument("name")
    p_del.set_defaults(func=cmd_delete)

    p_diff = sub.add_parser("diff", help="Diff two snapshots or snapshot vs current env.")
    p_diff.add_argument("base", help="Base snapshot name.")
    p_diff.add_argument("target", nargs="?", default=None, help="Target snapshot (default: current env).")
    p_diff.set_defaults(func=cmd_diff)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
