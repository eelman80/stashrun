"""CLI commands for snapshot momentum scoring."""

import argparse
from stashrun.snapshots_momentum import compute_momentum, momentum_rank, momentum_summary


def cmd_momentum_show(args: argparse.Namespace) -> None:
    result = compute_momentum(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Momentum for '{args.name}':")
    print(f"  Version score : {result['version_score']}")
    print(f"  Access score  : {result['access_score']}")
    print(f"  Rating score  : {result['rating_score']}")
    print(f"  Recency score : {result['recency_score']}")
    print(f"  Total         : {result['total']}")


def cmd_momentum_top(args: argparse.Namespace) -> None:
    ranked = momentum_rank()
    limit = getattr(args, "limit", 10)
    if not ranked:
        print("No snapshots found.")
        return
    print(f"Top {limit} snapshots by momentum:")
    for entry in ranked[:limit]:
        print(f"  {entry['name']:30s}  score={entry['total']}")


def cmd_momentum_summary(args: argparse.Namespace) -> None:
    summary = momentum_summary()
    print(f"Snapshots : {summary['count']}")
    print(f"Average   : {summary['average']}")
    print(f"Top       : {summary['top'] or 'N/A'}")


def register_momentum_commands(subparsers) -> None:
    p_show = subparsers.add_parser("momentum-show", help="Show momentum score for a snapshot")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_momentum_show)

    p_top = subparsers.add_parser("momentum-top", help="List snapshots ranked by momentum")
    p_top.add_argument("--limit", type=int, default=10)
    p_top.set_defaults(func=cmd_momentum_top)

    p_sum = subparsers.add_parser("momentum-summary", help="Overall momentum statistics")
    p_sum.set_defaults(func=cmd_momentum_summary)
