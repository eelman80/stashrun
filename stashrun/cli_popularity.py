"""CLI commands for snapshot popularity scoring."""

from stashrun.snapshots_popularity import compute_popularity, popularity_rank, popularity_summary


def cmd_popularity_show(args):
    result = compute_popularity(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Popularity for '{args.name}':")
    print(f"  Access score   : {result['access_score']}")
    print(f"  Favorite score : {result['favorite_score']}")
    print(f"  Reaction score : {result['reaction_score']}")
    print(f"  Rating score   : {result['rating_score']}")
    print(f"  Total          : {result['total']}")


def cmd_popularity_top(args):
    ranked = popularity_rank()
    limit = getattr(args, "limit", 10)
    if not ranked:
        print("No snapshots found.")
        return
    print(f"Top {limit} snapshots by popularity:")
    for entry in ranked[:limit]:
        print(f"  {entry['name']}: {entry['total']}")


def cmd_popularity_summary(args):
    summary = popularity_summary()
    print(f"Total snapshots : {summary['count']}")
    print(f"Average score   : {summary['average']}")
    print(f"Top snapshot    : {summary['top'] or 'N/A'}")


def register_popularity_commands(subparsers):
    p = subparsers.add_parser("popularity", help="Snapshot popularity commands")
    sub = p.add_subparsers(dest="popularity_cmd")

    show = sub.add_parser("show", help="Show popularity score for a snapshot")
    show.add_argument("name")
    show.set_defaults(func=cmd_popularity_show)

    top = sub.add_parser("top", help="List top snapshots by popularity")
    top.add_argument("--limit", type=int, default=10)
    top.set_defaults(func=cmd_popularity_top)

    summ = sub.add_parser("summary", help="Show popularity summary statistics")
    summ.set_defaults(func=cmd_popularity_summary)
