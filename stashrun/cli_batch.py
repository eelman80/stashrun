"""CLI commands for batch snapshot operations."""

import argparse
from stashrun.snapshots_batch import batch_delete, batch_copy, batch_tag_delete, batch_export_names


def cmd_batch_delete(args: argparse.Namespace) -> None:
    names = args.names
    results = batch_delete(names)
    for name, ok in results.items():
        status = "deleted" if ok else "not found"
        print(f"  {name}: {status}")


def cmd_batch_copy(args: argparse.Namespace) -> None:
    if len(args.pairs) % 2 != 0:
        print("Error: pairs must be provided as SRC DST SRC DST ...")
        return
    pairs = [(args.pairs[i], args.pairs[i + 1]) for i in range(0, len(args.pairs), 2)]
    results = batch_copy(pairs, overwrite=args.overwrite)
    for key, ok in results.items():
        status = "copied" if ok else "failed"
        print(f"  {key}: {status}")


def cmd_batch_tag_delete(args: argparse.Namespace) -> None:
    results = batch_tag_delete(args.tag)
    if not results:
        print(f"No snapshots found with tag '{args.tag}'.")
        return
    for name, ok in results.items():
        status = "deleted" if ok else "failed"
        print(f"  {name}: {status}")


def cmd_batch_list(args: argparse.Namespace) -> None:
    names = batch_export_names(pattern=args.pattern)
    if not names:
        print("No snapshots found.")
        return
    for name in names:
        print(f"  {name}")


def register_batch_commands(subparsers) -> None:
    p_del = subparsers.add_parser("batch-delete", help="Delete multiple snapshots")
    p_del.add_argument("names", nargs="+")
    p_del.set_defaults(func=cmd_batch_delete)

    p_copy = subparsers.add_parser("batch-copy", help="Copy multiple snapshots")
    p_copy.add_argument("pairs", nargs="+", metavar="SRC_or_DST")
    p_copy.add_argument("--overwrite", action="store_true")
    p_copy.set_defaults(func=cmd_batch_copy)

    p_tdel = subparsers.add_parser("batch-tag-delete", help="Delete all snapshots with a tag")
    p_tdel.add_argument("tag")
    p_tdel.set_defaults(func=cmd_batch_tag_delete)

    p_list = subparsers.add_parser("batch-list", help="List snapshots with optional filter")
    p_list.add_argument("--pattern", default=None)
    p_list.set_defaults(func=cmd_batch_list)
