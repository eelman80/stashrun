"""CLI commands for snapshot bookmarks."""

from stashrun.snapshots_bookmarks import (
    set_bookmark, remove_bookmark, resolve_bookmark,
    list_bookmarks, rename_bookmark,
)


def cmd_bookmark_set(args):
    set_bookmark(args.alias, args.snapshot)
    print(f"Bookmark '{args.alias}' -> '{args.snapshot}'")


def cmd_bookmark_remove(args):
    if remove_bookmark(args.alias):
        print(f"Removed bookmark '{args.alias}'")
    else:
        print(f"Bookmark '{args.alias}' not found")


def cmd_bookmark_resolve(args):
    name = resolve_bookmark(args.alias)
    if name:
        print(name)
    else:
        print(f"No bookmark named '{args.alias}'")


def cmd_bookmark_list(args):
    bm = list_bookmarks()
    if not bm:
        print("No bookmarks set")
        return
    for alias, snapshot in sorted(bm.items()):
        print(f"{alias} -> {snapshot}")


def cmd_bookmark_rename(args):
    if rename_bookmark(args.old, args.new):
        print(f"Renamed bookmark '{args.old}' to '{args.new}'")
    else:
        print(f"Bookmark '{args.old}' not found")


def register_bookmark_commands(subparsers):
    p = subparsers.add_parser("bookmark-set", help="Set a bookmark")
    p.add_argument("alias")
    p.add_argument("snapshot")
    p.set_defaults(func=cmd_bookmark_set)

    p = subparsers.add_parser("bookmark-remove", help="Remove a bookmark")
    p.add_argument("alias")
    p.set_defaults(func=cmd_bookmark_remove)

    p = subparsers.add_parser("bookmark-resolve", help="Resolve a bookmark")
    p.add_argument("alias")
    p.set_defaults(func=cmd_bookmark_resolve)

    p = subparsers.add_parser("bookmark-list", help="List all bookmarks")
    p.set_defaults(func=cmd_bookmark_list)

    p = subparsers.add_parser("bookmark-rename", help="Rename a bookmark")
    p.add_argument("old")
    p.add_argument("new")
    p.set_defaults(func=cmd_bookmark_rename)
