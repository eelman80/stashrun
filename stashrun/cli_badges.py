"""CLI commands for snapshot badges."""

from stashrun.snapshots_badges import compute_badges, badge_summary, snapshots_with_badge, BADGES
from stashrun.snapshot import list_all_snapshots


def cmd_badges_show(args):
    badges = badge_summary(args.name)
    if badges is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    if not badges:
        print(f"No badges earned by '{args.name}'.")
        return
    for key, label in badges.items():
        print(f"  [{key}] {label}")


def cmd_badges_find(args):
    if args.badge not in BADGES:
        print(f"Unknown badge '{args.badge}'. Available: {', '.join(BADGES)}.")
        return
    names = list_all_snapshots()
    matches = snapshots_with_badge(args.badge, names)
    if not matches:
        print(f"No snapshots with badge '{args.badge}'.")
        return
    for name in matches:
        print(name)


def cmd_badges_list_types(args):
    for key, label in BADGES.items():
        print(f"  {key}: {label}")


def register_badges_commands(subparsers):
    p_show = subparsers.add_parser("badges-show", help="Show badges for a snapshot")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_badges_show)

    p_find = subparsers.add_parser("badges-find", help="Find snapshots with a badge")
    p_find.add_argument("badge")
    p_find.set_defaults(func=cmd_badges_find)

    p_list = subparsers.add_parser("badges-list", help="List all badge types")
    p_list.set_defaults(func=cmd_badges_list_types)
