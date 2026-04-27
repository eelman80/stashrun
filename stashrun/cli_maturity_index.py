"""CLI commands for snapshot maturity index."""

from stashrun.snapshots_maturity_index import (
    compute_maturity_index,
    maturity_index_rank,
    maturity_index_summary,
)


def cmd_maturity_index_show(args) -> None:
    """Show the maturity index breakdown for a single snapshot."""
    result = compute_maturity_index(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Maturity Index: {result['name']}")
    print(f"  Maturity  : {result['maturity']} (+{result['maturity_score']}pts)")
    print(f"  Lifecycle : {result['lifecycle']} (+{result['lifecycle_score']}pts)")
    print(f"  Status    : {result['status']} (+{result['status_score']}pts)")
    print(f"  Versions  : {result['version_count']} (+{result['version_score']}pts)")
    print(f"  Total     : {result['total']} / 160")


def cmd_maturity_index_top(args) -> None:
    """List snapshots ranked by maturity index."""
    ranked = maturity_index_rank()
    limit = getattr(args, "limit", 10)
    if not ranked:
        print("No snapshots found.")
        return
    for i, entry in enumerate(ranked[:limit], 1):
        print(f"{i:>3}. {entry['name']:<30} score={entry['total']}")


def cmd_maturity_index_summary(args) -> None:
    """Print aggregate maturity index summary."""
    summary = maturity_index_summary()
    if summary["count"] == 0:
        print("No snapshots available.")
        return
    print(f"Snapshots : {summary['count']}")
    print(f"Average   : {summary['average']}")
    print(f"Top       : {summary['top']}")


def register_maturity_index_commands(subparsers) -> None:
    """Register maturity-index subcommands onto a subparsers object."""
    p_show = subparsers.add_parser("maturity-index", help="Show maturity index for a snapshot")
    p_show.add_argument("name", help="Snapshot name")
    p_show.set_defaults(func=cmd_maturity_index_show)

    p_top = subparsers.add_parser("maturity-index-top", help="Rank snapshots by maturity index")
    p_top.add_argument("--limit", type=int, default=10, help="Max results")
    p_top.set_defaults(func=cmd_maturity_index_top)

    p_sum = subparsers.add_parser("maturity-index-summary", help="Aggregate maturity index stats")
    p_sum.set_defaults(func=cmd_maturity_index_summary)
