"""CLI commands for snapshot freshness scoring."""

from stashrun.snapshots_freshness import compute_freshness, freshness_rank, freshness_summary
from stashrun.snapshot import list_all_snapshots


def cmd_freshness_show(args):
    name = args.name
    result = compute_freshness(name)
    if result is None:
        print(f"Snapshot '{name}' not found.")
        return
    print(f"Freshness for '{name}':")
    print(f"  Age score:    {result['age_score']}")
    print(f"  Access score: {result['access_score']}")
    print(f"  Save score:   {result['save_score']}")
    print(f"  Total:        {result['total']} / 100")


def cmd_freshness_top(args):
    limit = getattr(args, "limit", 5)
    names = list_all_snapshots()
    ranked = freshness_rank(names)
    if not ranked:
        print("No snapshots found.")
        return
    print("Top snapshots by freshness:")
    for i, (name, score) in enumerate(ranked[:limit], 1):
        print(f"  {i}. {name} — {score}/100")


def cmd_freshness_summary(args):
    names = list_all_snapshots()
    summary = freshness_summary(names)
    print(f"Snapshots evaluated: {summary['count']}")
    print(f"Average freshness:   {summary['average']}")
    print(f"Top freshness:       {summary['top']}")


def register_freshness_commands(subparsers):
    p = subparsers.add_parser("freshness", help="Snapshot freshness scoring")
    sub = p.add_subparsers(dest="freshness_cmd")

    show_p = sub.add_parser("show", help="Show freshness score for a snapshot")
    show_p.add_argument("name")
    show_p.set_defaults(func=cmd_freshness_show)

    top_p = sub.add_parser("top", help="List top snapshots by freshness")
    top_p.add_argument("--limit", type=int, default=5)
    top_p.set_defaults(func=cmd_freshness_top)

    sum_p = sub.add_parser("summary", help="Freshness summary across all snapshots")
    sum_p.set_defaults(func=cmd_freshness_summary)
