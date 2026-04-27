"""CLI commands for snapshot gravity scores."""

from __future__ import annotations

import argparse

from stashrun.snapshots_gravity import compute_gravity, gravity_rank, gravity_summary


def cmd_gravity_show(args: argparse.Namespace) -> None:
    result = compute_gravity(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Gravity score for '{args.name}': {result['total']}")
    print(f"  Dependents   : {result['dependents']} (+{result['dep_score']} pts)")
    print(f"  Mentions     : {result['mentions']} (+{result['mention_score']} pts)")
    print(f"  Relations    : {result['relations']} (+{result['relation_score']} pts)")
    print(f"  Endorsements : {result['endorsements']} (+{result['endorse_score']} pts)")


def cmd_gravity_top(args: argparse.Namespace) -> None:
    ranked = gravity_rank()
    limit = args.limit if hasattr(args, "limit") and args.limit else 10
    if not ranked:
        print("No snapshots found.")
        return
    for entry in ranked[:limit]:
        print(f"{entry['name']:<30} {entry['total']:>4}")


def cmd_gravity_summary(args: argparse.Namespace) -> None:
    summary = gravity_summary()
    if summary["count"] == 0:
        print("No snapshots available.")
        return
    print(f"Snapshots : {summary['count']}")
    print(f"Avg score : {summary['avg']}")
    print(f"Max score : {summary['max']}")
    print(f"Top       : {summary['top']}")


def register_gravity_commands(subparsers) -> None:
    p_show = subparsers.add_parser("gravity-show", help="Show gravity score for a snapshot")
    p_show.add_argument("name", help="Snapshot name")
    p_show.set_defaults(func=cmd_gravity_show)

    p_top = subparsers.add_parser("gravity-top", help="List snapshots ranked by gravity")
    p_top.add_argument("--limit", type=int, default=10, help="Number of results")
    p_top.set_defaults(func=cmd_gravity_top)

    p_sum = subparsers.add_parser("gravity-summary", help="Aggregate gravity statistics")
    p_sum.set_defaults(func=cmd_gravity_summary)
