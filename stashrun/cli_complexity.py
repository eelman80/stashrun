"""CLI commands for snapshot complexity analysis."""

from stashrun.snapshots_complexity import compute_complexity, complexity_rank, complexity_summary
from stashrun.snapshot import list_all_snapshots


def cmd_complexity_show(args):
    result = compute_complexity(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Snapshot : {result['name']}")
    print(f"Keys     : {result['key_count']}")
    print(f"Avg value length: {result['avg_value_length']}")
    print(f"Long values ({len(result['long_value_keys'])}): {', '.join(result['long_value_keys']) or 'none'}")
    print(f"Prefixes : {result['prefix_count']}")
    print(f"Tags     : {result['tag_count']}")
    print(f"Score    : {result['score']}")


def cmd_complexity_top(args):
    names = list_all_snapshots()
    limit = getattr(args, "limit", 5)
    ranked = complexity_rank(names)[:limit]
    if not ranked:
        print("No snapshots found.")
        return
    for r in ranked:
        print(f"{r['name']:30s}  score={r['score']}  keys={r['key_count']}")


def cmd_complexity_summary(args):
    names = list_all_snapshots()
    summary = complexity_summary(names)
    print(f"Snapshots : {summary['count']}")
    print(f"Avg score : {summary['avg_score']}")
    print(f"Max score : {summary['max_score']}")
    print(f"Min score : {summary['min_score']}")


def register_complexity_commands(subparsers):
    p = subparsers.add_parser("complexity", help="Snapshot complexity tools")
    sub = p.add_subparsers(dest="complexity_cmd")

    show = sub.add_parser("show", help="Show complexity of a snapshot")
    show.add_argument("name")
    show.set_defaults(func=cmd_complexity_show)

    top = sub.add_parser("top", help="List top N most complex snapshots")
    top.add_argument("--limit", type=int, default=5)
    top.set_defaults(func=cmd_complexity_top)

    summ = sub.add_parser("summary", help="Aggregate complexity summary")
    summ.set_defaults(func=cmd_complexity_summary)
