"""CLI commands for managing snapshot favorites."""

from stashrun.snapshots_favorites import (
    add_favorite, remove_favorite, list_favorites, is_favorite, clear_favorites
)


def cmd_favorite_add(args):
    if add_favorite(args.name):
        print(f"Added '{args.name}' to favorites.")
    else:
        print(f"'{args.name}' is already a favorite.")


def cmd_favorite_remove(args):
    if remove_favorite(args.name):
        print(f"Removed '{args.name}' from favorites.")
    else:
        print(f"'{args.name}' is not in favorites.")


def cmd_favorite_list(args):
    favs = list_favorites()
    if not favs:
        print("No favorites saved.")
    else:
        for name in favs:
            print(name)


def cmd_favorite_check(args):
    if is_favorite(args.name):
        print(f"'{args.name}' is a favorite.")
    else:
        print(f"'{args.name}' is not a favorite.")


def cmd_favorite_clear(args):
    count = clear_favorites()
    print(f"Cleared {count} favorite(s).")


def register_favorite_commands(subparsers):
    p = subparsers.add_parser("favorite", help="Manage favorite snapshots")
    sub = p.add_subparsers(dest="favorite_cmd")

    add_p = sub.add_parser("add", help="Add a snapshot to favorites")
    add_p.add_argument("name")
    add_p.set_defaults(func=cmd_favorite_add)

    rm_p = sub.add_parser("remove", help="Remove a snapshot from favorites")
    rm_p.add_argument("name")
    rm_p.set_defaults(func=cmd_favorite_remove)

    list_p = sub.add_parser("list", help="List all favorites")
    list_p.set_defaults(func=cmd_favorite_list)

    check_p = sub.add_parser("check", help="Check if a snapshot is a favorite")
    check_p.add_argument("name")
    check_p.set_defaults(func=cmd_favorite_check)

    clear_p = sub.add_parser("clear", help="Clear all favorites")
    clear_p.set_defaults(func=cmd_favorite_clear)
