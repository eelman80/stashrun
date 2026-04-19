"""CLI commands for snapshot impact scoring."""

import argparse
from stashrun.snapshots_impact import compute_impact, impact_rank, impact_summary
from stashrun.snapshot import list_all_snapshots


def cmd_impact_show(args: argparse.Namespace) -> None:
    result = compute_impact(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Impact for '{args.name}':")
    print(f"  Dependents  : {result['dependents']} (score: {result['dependent_score']})")
    print(f"  Subscribers : {result['subscribers']} (score: {result['subscriber_score']})")
    print(f"  Groups      : {result['groups']} (score: {result['group_score']})")
    print(f"  Total       : {result['total']} / 100")


def cmd_impact_top(args: argparse.Namespace) -> None:
    names = list_all_snapshots()
    ranked = impact_rank(names)
    limit = getattr(args, "limit", 5)
    if not ranked:
        print("No snapshots found.")
        return
    for entry in ranked[:limit]:
        print(f"{entry['name']}: {entry['total']}")


def cmd_impact_summary(args: argparse.Namespace) -> None:
    names = list_all_snapshots()
    summary = impact_summary(names)
    print(f"Snapshots : {summary['count']}")
    print(f"Avg Impact: {summary['avg_total']}")
    print(f"Max Impact: {summary['max_total']}")


def register_impact_commands(subparsers) -> None:
    p_show = subparsers.add_parser("impact-show", help="Show impact score for a snapshot")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_impact_show)

    p_top = subparsers.add_parser("impact-top", help="List top snapshots by impact")
    p_top.add_argument("--limit", type=int, default=5)
    p_top.set_defaults(func=cmd_impact_top)

    p_sum = subparsers.add_parser("impact-summary", help="Summarise impact across all snapshots")
    p_sum.set_defaults(func=cmd_impact_summary)
