"""CLI commands for snapshot volatility analysis."""

from __future__ import annotations

import argparse

from stashrun.snapshots_volatility import (
    compute_volatility,
    volatility_rank,
    volatility_summary,
)
from stashrun.storage import list_snapshots


def cmd_volatility_show(args: argparse.Namespace) -> None:
    result = compute_volatility(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Snapshot : {result['name']}")
    print(f"Versions : {result['version_count']}")
    print(f"Key churn: {result['key_churn']}")
    print(f"Accesses : {result['access_count']}")
    print(f"Score    : {result['volatility_score']}/100")


def cmd_volatility_top(args: argparse.Namespace) -> None:
    names = list_snapshots()
    ranked = volatility_rank(names)
    limit = getattr(args, "limit", 10)
    if not ranked:
        print("No snapshots found.")
        return
    for entry in ranked[:limit]:
        print(f"{entry['volatility_score']:>3}  {entry['name']}")


def cmd_volatility_summary(args: argparse.Namespace) -> None:
    names = list_snapshots()
    summary = volatility_summary(names)
    if summary["count"] == 0:
        print("No snapshots to summarise.")
        return
    print(f"Snapshots : {summary['count']}")
    print(f"Avg score : {summary['avg_score']}")
    print(f"Max score : {summary['max_score']}")
    print(f"Min score : {summary['min_score']}")


def register_volatility_commands(subparsers: argparse._SubParsersAction) -> None:
    p_show = subparsers.add_parser("volatility-show", help="Show volatility profile for a snapshot")
    p_show.add_argument("name", help="Snapshot name")
    p_show.set_defaults(func=cmd_volatility_show)

    p_top = subparsers.add_parser("volatility-top", help="List snapshots by volatility score")
    p_top.add_argument("--limit", type=int, default=10, help="Number of results")
    p_top.set_defaults(func=cmd_volatility_top)

    p_sum = subparsers.add_parser("volatility-summary", help="Aggregate volatility stats")
    p_sum.set_defaults(func=cmd_volatility_summary)
