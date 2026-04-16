"""CLI commands for snapshot statistics."""
from __future__ import annotations
import argparse
from stashrun.snapshots_stats import summary, most_common_keys, snapshot_count


def cmd_stats(args: argparse.Namespace) -> None:
    data = summary()
    print(f"Snapshots : {data['total_snapshots']}")
    print(f"Total keys: {data['total_keys']}")
    print(f"Avg keys  : {data['average_keys']}")
    print(f"Tagged    : {data['tagged']}")
    print(f"Pinned    : {data['pinned']}")
    if data["most_common_keys"]:
        print("Top keys  :")
        for key, count in data["most_common_keys"]:
            print(f"  {key}: {count}")
    else:
        print("Top keys  : (none)")


def cmd_stats_keys(args: argparse.Namespace) -> None:
    top_n = getattr(args, "top", 10)
    results = most_common_keys(top_n)
    if not results:
        print("No snapshots found.")
        return
    for key, count in results:
        print(f"{key}: {count}")


def register_stats_commands(subparsers) -> None:
    p_stats = subparsers.add_parser("stats", help="Show snapshot statistics")
    p_stats.set_defaults(func=cmd_stats)

    p_keys = subparsers.add_parser("stats-keys", help="Show most common env keys")
    p_keys.add_argument("--top", type=int, default=10, help="Number of results")
    p_keys.set_defaults(func=cmd_stats_keys)
