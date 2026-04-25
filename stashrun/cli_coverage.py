"""CLI commands for snapshot key coverage analysis."""

from __future__ import annotations

import argparse

from stashrun.snapshots_coverage import compute_coverage, coverage_rank, coverage_summary


def cmd_coverage_show(args: argparse.Namespace) -> None:
    """Show coverage of a single snapshot against a reference key list."""
    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        print("Error: --keys must be a non-empty comma-separated list.")
        return

    result = compute_coverage(args.name, keys)
    if result is None:
        print(f"Snapshot '{args.name}' not found or no reference keys provided.")
        return

    print(f"Coverage for '{args.name}': {result['coverage_pct']}%")
    print(f"  Reference keys : {result['total_reference']}")
    print(f"  Covered        : {len(result['covered'])}  {result['covered']}")
    print(f"  Missing        : {len(result['missing'])}  {result['missing']}")
    print(f"  Extra keys     : {len(result['extra'])}  {result['extra']}")


def cmd_coverage_top(args: argparse.Namespace) -> None:
    """Rank snapshots by coverage against a reference key list."""
    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        print("Error: --keys must be a non-empty comma-separated list.")
        return

    ranked = coverage_rank(keys)
    if not ranked:
        print("No snapshots found.")
        return

    limit = getattr(args, "limit", 10)
    for entry in ranked[:limit]:
        print(f"{entry['coverage_pct']:6.2f}%  {entry['name']}")


def cmd_coverage_summary(args: argparse.Namespace) -> None:
    """Print aggregate coverage statistics across all snapshots."""
    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        print("Error: --keys must be a non-empty comma-separated list.")
        return

    summary = coverage_summary(keys)
    print(f"Snapshots analysed : {summary['count']}")
    print(f"Avg coverage       : {summary['avg_coverage_pct']}%")
    print(f"Full coverage (100%): {summary['full_coverage']}")


def register_coverage_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_show = subparsers.add_parser("coverage-show", help="Show key coverage for a snapshot")
    p_show.add_argument("name", help="Snapshot name")
    p_show.add_argument("--keys", required=True, help="Comma-separated reference key list")
    p_show.set_defaults(func=cmd_coverage_show)

    p_top = subparsers.add_parser("coverage-top", help="Rank snapshots by key coverage")
    p_top.add_argument("--keys", required=True, help="Comma-separated reference key list")
    p_top.add_argument("--limit", type=int, default=10, help="Max results (default 10)")
    p_top.set_defaults(func=cmd_coverage_top)

    p_sum = subparsers.add_parser("coverage-summary", help="Aggregate coverage statistics")
    p_sum.add_argument("--keys", required=True, help="Comma-separated reference key list")
    p_sum.set_defaults(func=cmd_coverage_summary)
