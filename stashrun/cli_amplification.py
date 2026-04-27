"""CLI commands for snapshot amplification scoring."""

from __future__ import annotations

from stashrun.snapshots_amplification import (
    compute_amplification,
    amplification_rank,
    amplification_summary,
)


def cmd_amplification_show(args) -> None:
    """Show amplification score for a single snapshot."""
    result = compute_amplification(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Amplification score for '{args.name}': {result['score']}/100")
    print(f"  Dependents : {result['dependents']}  (+{result['dep_score']} pts)")
    print(f"  Relations  : {result['relations']}  (+{result['rel_score']} pts)")
    print(f"  Groups     : {result['groups']}  (+{result['grp_score']} pts)")


def cmd_amplification_top(args) -> None:
    """List snapshots ranked by amplification score."""
    limit = getattr(args, "limit", 10)
    ranked = amplification_rank()[:limit]
    if not ranked:
        print("No snapshots found.")
        return
    for i, entry in enumerate(ranked, 1):
        print(f"{i:>3}. {entry['name']:<30} score={entry['score']}")


def cmd_amplification_summary(args) -> None:  # noqa: ARG001
    """Print aggregate amplification statistics."""
    summary = amplification_summary()
    if summary["count"] == 0:
        print("No snapshots available.")
        return
    print(f"Snapshots analysed : {summary['count']}")
    print(f"Average score      : {summary['avg_score']}")
    print(f"Max score          : {summary['max_score']}")
    print(f"Top snapshot       : {summary['top']}")


def register_amplification_commands(subparsers) -> None:
    """Attach amplification sub-commands to *subparsers*."""
    p = subparsers.add_parser("amplification", help="Amplification scoring")
    sub = p.add_subparsers(dest="amplification_cmd")

    show_p = sub.add_parser("show", help="Show score for a snapshot")
    show_p.add_argument("name")
    show_p.set_defaults(func=cmd_amplification_show)

    top_p = sub.add_parser("top", help="Rank snapshots by amplification")
    top_p.add_argument("--limit", type=int, default=10)
    top_p.set_defaults(func=cmd_amplification_top)

    sum_p = sub.add_parser("summary", help="Aggregate amplification stats")
    sum_p.set_defaults(func=cmd_amplification_summary)
