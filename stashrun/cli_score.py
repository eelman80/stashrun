"""CLI commands for composite snapshot scoring."""

import argparse
from stashrun.snapshots_score import compute_score, score_rank, score_summary
from stashrun.snapshot import list_all_snapshots


def cmd_score_show(args: argparse.Namespace) -> None:
    result = compute_score(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Composite score for '{args.name}': {result['composite']}")
    print(f"  Health:     {result['health']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Reputation: {result['reputation']}")
    print(f"  Impact:     {result['impact']}")


def cmd_score_top(args: argparse.Namespace) -> None:
    names = list_all_snapshots()
    ranked = score_rank(names)
    limit = getattr(args, "limit", 5)
    if not ranked:
        print("No snapshots scored.")
        return
    for entry in ranked[:limit]:
        print(f"{entry['name']}: {entry['composite']}")


def cmd_score_summary(args: argparse.Namespace) -> None:
    names = list_all_snapshots()
    summary = score_summary(names)
    if summary["count"] == 0:
        print("No snapshots available.")
        return
    print(f"Snapshots scored: {summary['count']}")
    print(f"Average composite: {summary['average']}")
    print(f"Top snapshot: {summary['top']}")


def register_score_commands(subparsers) -> None:
    p_show = subparsers.add_parser("score-show", help="Show composite score for a snapshot")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_score_show)

    p_top = subparsers.add_parser("score-top", help="List top-scored snapshots")
    p_top.add_argument("--limit", type=int, default=5)
    p_top.set_defaults(func=cmd_score_top)

    p_sum = subparsers.add_parser("score-summary", help="Aggregate score summary")
    p_sum.set_defaults(func=cmd_score_summary)
