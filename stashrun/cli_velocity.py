"""CLI commands for snapshot velocity."""

from __future__ import annotations

from stashrun.snapshots_velocity import compute_velocity, velocity_rank, velocity_summary


def cmd_velocity_show(args) -> None:
    """Show velocity metrics for a single snapshot."""
    data = compute_velocity(args.name)
    if data is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Velocity — {args.name}")
    print(f"  Versions     : {data['version_count']}")
    print(f"  Accesses     : {data['access_count']}")
    print(f"  Version score: {data['version_score']}")
    print(f"  Access score : {data['access_score']}")
    print(f"  Recency bonus: {data['recency_bonus']}")
    print(f"  Total score  : {data['score']} / 100")


def cmd_velocity_top(args) -> None:
    """List snapshots ranked by velocity score."""
    limit = getattr(args, "limit", 10)
    ranked = velocity_rank()[:limit]
    if not ranked:
        print("No snapshots found.")
        return
    print(f"{'Rank':<5} {'Name':<30} {'Score':>5}")
    print("-" * 42)
    for i, (name, score) in enumerate(ranked, 1):
        print(f"{i:<5} {name:<30} {score:>5}")


def cmd_velocity_summary(args) -> None:  # noqa: ARG001
    """Print aggregate velocity summary."""
    summary = velocity_summary()
    print(f"Total snapshots : {summary['count']}")
    print(f"Average score   : {summary['avg_score']}")
    print(f"Top snapshot    : {summary['top'] or 'N/A'}")


def register_velocity_commands(subparsers) -> None:
    p = subparsers.add_parser("velocity", help="Snapshot velocity commands")
    sub = p.add_subparsers(dest="velocity_cmd")

    show_p = sub.add_parser("show", help="Show velocity for a snapshot")
    show_p.add_argument("name")
    show_p.set_defaults(func=cmd_velocity_show)

    top_p = sub.add_parser("top", help="List top snapshots by velocity")
    top_p.add_argument("--limit", type=int, default=10)
    top_p.set_defaults(func=cmd_velocity_top)

    summary_p = sub.add_parser("summary", help="Aggregate velocity summary")
    summary_p.set_defaults(func=cmd_velocity_summary)
