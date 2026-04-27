"""CLI commands for snapshot resilience scoring."""

import argparse
from stashrun.snapshots_resilience import (
    compute_resilience,
    resilience_rank,
    resilience_summary,
)


def cmd_resilience_show(args: argparse.Namespace) -> None:
    result = compute_resilience(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Resilience score for '{args.name}': {result['score']}/100")
    for key, val in result["details"].items():
        print(f"  {key}: {val}")


def cmd_resilience_top(args: argparse.Namespace) -> None:
    ranked = resilience_rank()
    limit = getattr(args, "limit", 10)
    if not ranked:
        print("No snapshots found.")
        return
    for name, score in ranked[:limit]:
        print(f"  {name}: {score}")


def cmd_resilience_summary(args: argparse.Namespace) -> None:
    summary = resilience_summary()
    if summary["count"] == 0:
        print("No snapshots found.")
        return
    print(f"Snapshots:  {summary['count']}")
    print(f"Average:    {summary['average']}")
    print(f"Min:        {summary['min']}")
    print(f"Max:        {summary['max']}")


def register_resilience_commands(subparsers) -> None:
    p_show = subparsers.add_parser("resilience-show", help="Show resilience score")
    p_show.add_argument("name", help="Snapshot name")
    p_show.set_defaults(func=cmd_resilience_show)

    p_top = subparsers.add_parser("resilience-top", help="Top snapshots by resilience")
    p_top.add_argument("--limit", type=int, default=10)
    p_top.set_defaults(func=cmd_resilience_top)

    p_sum = subparsers.add_parser("resilience-summary", help="Resilience summary stats")
    p_sum.set_defaults(func=cmd_resilience_summary)
