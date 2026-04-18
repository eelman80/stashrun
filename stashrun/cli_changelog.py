"""CLI commands for snapshot changelog management."""

from stashrun.snapshots_changelog import (
    set_changelog,
    get_changelog,
    remove_changelog,
    list_changelogs,
    clear_changelogs,
)


def cmd_changelog_set(args) -> None:
    set_changelog(args.name, args.message)
    print(f"Changelog set for '{args.name}'.")


def cmd_changelog_get(args) -> None:
    msg = get_changelog(args.name)
    if msg is None:
        print(f"No changelog for '{args.name}'.")
    else:
        print(f"{args.name}: {msg}")


def cmd_changelog_remove(args) -> None:
    if remove_changelog(args.name):
        print(f"Changelog removed for '{args.name}'.")
    else:
        print(f"No changelog found for '{args.name}'.")


def cmd_changelog_list(args) -> None:
    entries = list_changelogs()
    if not entries:
        print("No changelog entries.")
        return
    for name, msg in entries.items():
        print(f"  {name}: {msg}")


def cmd_changelog_clear(args) -> None:
    count = clear_changelogs()
    print(f"Cleared {count} changelog entries.")


def register_changelog_commands(subparsers) -> None:
    p = subparsers.add_parser("changelog", help="Manage snapshot changelogs")
    sub = p.add_subparsers(dest="changelog_cmd")

    ps = sub.add_parser("set", help="Set changelog for a snapshot")
    ps.add_argument("name")
    ps.add_argument("message")
    ps.set_defaults(func=cmd_changelog_set)

    pg = sub.add_parser("get", help="Get changelog for a snapshot")
    pg.add_argument("name")
    pg.set_defaults(func=cmd_changelog_get)

    pr = sub.add_parser("remove", help="Remove changelog for a snapshot")
    pr.add_argument("name")
    pr.set_defaults(func=cmd_changelog_remove)

    pl = sub.add_parser("list", help="List all changelog entries")
    pl.set_defaults(func=cmd_changelog_list)

    pc = sub.add_parser("clear", help="Clear all changelog entries")
    pc.set_defaults(func=cmd_changelog_clear)
