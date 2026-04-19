"""CLI commands for snapshot confidence scoring."""

from stashrun.snapshots_confidence import compute_confidence, confidence_rank
from stashrun.snapshot import list_all_snapshots


def cmd_confidence_show(args):
    info = compute_confidence(args.name)
    if info is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Confidence for '{args.name}': {info['percent']}% ({info['score']}/{info['max_score']})")
    for key, val in info.items():
        if key not in ("score", "max_score", "percent"):
            print(f"  {key}: {val}")


def cmd_confidence_top(args):
    names = list_all_snapshots()
    ranked = confidence_rank(names)
    limit = getattr(args, "limit", 10) or 10
    if not ranked:
        print("No snapshots found.")
        return
    for name, pct in ranked[:limit]:
        print(f"{pct:6.1f}%  {name}")


def register_confidence_commands(subparsers):
    p_show = subparsers.add_parser("confidence-show", help="Show confidence score for a snapshot")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_confidence_show)

    p_top = subparsers.add_parser("confidence-top", help="List snapshots ranked by confidence")
    p_top.add_argument("--limit", type=int, default=10)
    p_top.set_defaults(func=cmd_confidence_top)
