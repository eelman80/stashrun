"""CLI commands for copying and renaming snapshots."""

import argparse
from stashrun.snapshots_copy import copy_snapshot, rename_snapshot


def cmd_copy(args: argparse.Namespace) -> None:
    ok = copy_snapshot(args.src, args.dst, overwrite=args.overwrite)
    if ok:
        print(f"Copied '{args.src}' -> '{args.dst}'")
    elif copy_snapshot.__doc__ and not ok:
        from stashrun.storage import load_snapshot, list_snapshots
        if load_snapshot(args.src) is None:
            print(f"Error: snapshot '{args.src}' not found.")
        elif args.dst in list_snapshots():
            print(f"Error: snapshot '{args.dst}' already exists. Use --overwrite to replace.")
        else:
            print("Error: copy failed.")


def cmd_rename(args: argparse.Namespace) -> None:
    ok = rename_snapshot(args.src, args.dst, overwrite=args.overwrite)
    if ok:
        print(f"Renamed '{args.src}' -> '{args.dst}'")
    else:
        from stashrun.storage import load_snapshot, list_snapshots
        if load_snapshot(args.src) is None:
            print(f"Error: snapshot '{args.src}' not found.")
        elif args.dst in list_snapshots():
            print(f"Error: snapshot '{args.dst}' already exists. Use --overwrite to replace.")
        else:
            print("Error: rename failed.")


def register_copy_commands(subparsers) -> None:
    p_copy = subparsers.add_parser("copy", help="Copy a snapshot to a new name")
    p_copy.add_argument("src", help="Source snapshot name")
    p_copy.add_argument("dst", help="Destination snapshot name")
    p_copy.add_argument("--overwrite", action="store_true", help="Overwrite destination if it exists")
    p_copy.set_defaults(func=cmd_copy)

    p_rename = subparsers.add_parser("rename", help="Rename a snapshot")
    p_rename.add_argument("src", help="Current snapshot name")
    p_rename.add_argument("dst", help="New snapshot name")
    p_rename.add_argument("--overwrite", action="store_true", help="Overwrite destination if it exists")
    p_rename.set_defaults(func=cmd_rename)
