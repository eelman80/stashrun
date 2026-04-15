"""CLI commands for side-by-side snapshot comparison."""

import argparse
from stashrun.snapshots_compare import (
    compare_snapshots,
    keys_unique_to,
    value_conflicts,
)


def cmd_compare(args: argparse.Namespace) -> None:
    """Print a side-by-side comparison table of two or more snapshots."""
    result = compare_snapshots(args.names)
    if not result["keys"]:
        print("No keys found in any of the specified snapshots.")
        return

    col_w = 28
    header = f"{'KEY':<30}" + "".join(f"{n:<{col_w}}" for n in result["snapshots"])
    print(header)
    print("-" * len(header))
    for key in result["keys"]:
        vals = result["matrix"][key]
        row = f"{key:<30}" + "".join(
            f"{(v if v is not None else '<absent>'):<{col_w}}" for v in vals
        )
        print(row)


def cmd_unique(args: argparse.Namespace) -> None:
    """Show keys present in TARGET but absent in all OTHER snapshots."""
    others = [n for n in args.names if n != args.target]
    unique = keys_unique_to(args.target, others)
    if not unique:
        print(f"No unique keys in '{args.target}'.")
        return
    print(f"Keys unique to '{args.target}':")
    for k, v in sorted(unique.items()):
        print(f"  {k}={v}")


def cmd_conflicts(args: argparse.Namespace) -> None:
    """Show keys shared by all snapshots where values differ."""
    conflicts = value_conflicts(args.names)
    if not conflicts:
        print("No conflicting values found.")
        return
    col_w = 28
    print(f"{'KEY':<30}" + "".join(f"{n:<{col_w}}" for n in args.names))
    print("-" * (30 + col_w * len(args.names)))
    for key, vals in sorted(conflicts.items()):
        row = f"{key:<30}" + "".join(
            f"{(v if v is not None else '<absent>'):<{col_w}}" for v in vals
        )
        print(row)


def register_compare_commands(subparsers) -> None:
    p_cmp = subparsers.add_parser("compare", help="Compare snapshots side-by-side")
    p_cmp.add_argument("names", nargs="+", metavar="SNAPSHOT")
    p_cmp.set_defaults(func=cmd_compare)

    p_uniq = subparsers.add_parser("unique", help="Keys unique to one snapshot")
    p_uniq.add_argument("target", metavar="TARGET")
    p_uniq.add_argument("names", nargs="+", metavar="SNAPSHOT")
    p_uniq.set_defaults(func=cmd_unique)

    p_conf = subparsers.add_parser("conflicts", help="Show value conflicts across snapshots")
    p_conf.add_argument("names", nargs="+", metavar="SNAPSHOT")
    p_conf.set_defaults(func=cmd_conflicts)
