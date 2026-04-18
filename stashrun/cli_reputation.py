"""CLI commands for snapshot reputation scoring."""

from stashrun.snapshots_reputation import compute_reputation, top_snapshots, reputation_summary


def cmd_reputation_score(args):
    """Show reputation score for a snapshot."""
    score = compute_reputation(args.name)
    print(f"Reputation score for '{args.name}': {score}/100")


def cmd_reputation_top(args):
    """List top snapshots by reputation."""
    n = getattr(args, "n", 5)
    results = top_snapshots(n)
    if not results:
        print("No snapshots found.")
        return
    print(f"Top {n} snapshots by reputation:")
    for rank, (name, score) in enumerate(results, 1):
        print(f"  {rank}. {name} — {score}/100")


def cmd_reputation_summary(args):
    """Show detailed reputation breakdown for a snapshot."""
    summary = reputation_summary(args.name)
    print(f"Reputation summary for '{args.name}':")
    print(f"  Score      : {summary['score']}/100")
    print(f"  Rating     : {summary['rating'] if summary['rating'] is not None else 'N/A'}")
    print(f"  Pinned     : {'yes' if summary['pinned'] else 'no'}")
    print(f"  Favorited  : {'yes' if summary['favorited'] else 'no'}")
    print(f"  Access count: {summary['access_count']}")


def register_reputation_commands(subparsers):
    p_score = subparsers.add_parser("reputation-score", help="Show reputation score for a snapshot")
    p_score.add_argument("name")
    p_score.set_defaults(func=cmd_reputation_score)

    p_top = subparsers.add_parser("reputation-top", help="List top snapshots by reputation")
    p_top.add_argument("--n", type=int, default=5, help="Number of results")
    p_top.set_defaults(func=cmd_reputation_top)

    p_summary = subparsers.add_parser("reputation-summary", help="Show reputation breakdown")
    p_summary.add_argument("name")
    p_summary.set_defaults(func=cmd_reputation_summary)
