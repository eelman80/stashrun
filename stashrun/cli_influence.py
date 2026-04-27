"""CLI commands for snapshot influence scoring."""

from stashrun.snapshots_influence import compute_influence, influence_rank, influence_summary


def cmd_influence_show(args) -> None:
    """Show the influence breakdown for a single snapshot."""
    info = compute_influence(args.name)
    if info is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Influence report: {info['name']}")
    print(f"  Dependents   : {info['dependents']}  (+{info['dep_score']} pts)")
    print(f"  Subscribers  : {info['subscribers']}  (+{info['sub_score']} pts)")
    print(f"  Mentions     : {info['mentions']}  (+{info['mention_score']} pts)")
    print(f"  Endorsements : {info['endorsements']}  (+{info['endorse_score']} pts)")
    print(f"  Total score  : {info['total']} / 100")


def cmd_influence_top(args) -> None:
    """List snapshots ranked by influence score."""
    limit = getattr(args, "limit", 10)
    ranked = influence_rank()[:limit]
    if not ranked:
        print("No snapshots found.")
        return
    print(f"{'Rank':<5} {'Name':<30} {'Score':>6}")
    print("-" * 44)
    for i, entry in enumerate(ranked, 1):
        print(f"{i:<5} {entry['name']:<30} {entry['total']:>6}")


def cmd_influence_summary(args) -> None:
    """Print aggregate influence statistics."""
    summary = influence_summary()
    if summary["count"] == 0:
        print("No snapshots available.")
        return
    print(f"Snapshots analysed : {summary['count']}")
    print(f"Average influence  : {summary['avg']}")
    print(f"Highest score      : {summary['max']}")
    print(f"Top snapshot       : {summary['top']}")


def register_influence_commands(subparsers) -> None:
    """Attach influence sub-commands to a parent argument parser."""
    p = subparsers.add_parser("influence", help="Snapshot influence scoring")
    sub = p.add_subparsers(dest="influence_cmd", required=True)

    show = sub.add_parser("show", help="Show influence for a snapshot")
    show.add_argument("name")
    show.set_defaults(func=cmd_influence_show)

    top = sub.add_parser("top", help="Rank snapshots by influence")
    top.add_argument("--limit", type=int, default=10)
    top.set_defaults(func=cmd_influence_top)

    summ = sub.add_parser("summary", help="Aggregate influence stats")
    summ.set_defaults(func=cmd_influence_summary)
