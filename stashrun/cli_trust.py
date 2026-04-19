"""CLI commands for snapshot trust scoring."""

from stashrun.snapshots_trust import compute_trust, trust_rank, trust_summary
from stashrun.snapshot import list_all_snapshots


def cmd_trust_show(args):
    result = compute_trust(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Trust score for '{args.name}': {result['score']}/100 ({result['level']})")
    for key, val in result["breakdown"].items():
        print(f"  {key}: +{val}")


def cmd_trust_top(args):
    names = list_all_snapshots()
    ranked = trust_rank(names)
    limit = getattr(args, "limit", 10)
    if not ranked:
        print("No snapshots found.")
        return
    for name, score in ranked[:limit]:
        print(f"{name}: {score}")


def cmd_trust_summary(args):
    names = list_all_snapshots()
    summary = trust_summary(names)
    for level, count in summary.items():
        print(f"{level}: {count}")


def register_trust_commands(subparsers):
    p = subparsers.add_parser("trust", help="Trust scoring commands")
    sub = p.add_subparsers(dest="trust_cmd")

    show = sub.add_parser("show", help="Show trust score for a snapshot")
    show.add_argument("name")
    show.set_defaults(func=cmd_trust_show)

    top = sub.add_parser("top", help="List snapshots by trust score")
    top.add_argument("--limit", type=int, default=10)
    top.set_defaults(func=cmd_trust_top)

    summary = sub.add_parser("summary", help="Trust level distribution")
    summary.set_defaults(func=cmd_trust_summary)
