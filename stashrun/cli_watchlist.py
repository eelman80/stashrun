"""CLI commands for managing the environment variable watchlist."""

import argparse
from stashrun.watchlist import watch_key, unwatch_key, get_watched_keys, is_watched


def cmd_watch_add(args: argparse.Namespace) -> None:
    added = watch_key(args.key, label=getattr(args, "label", None))
    if added:
        print(f"Watching: {args.key}")
    else:
        print(f"Already watched: {args.key}")


def cmd_watch_remove(args: argparse.Namespace) -> None:
    removed = unwatch_key(args.key)
    if removed:
        print(f"Removed from watchlist: {args.key}")
    else:
        print(f"Key not in watchlist: {args.key}")


def cmd_watch_list(args: argparse.Namespace) -> None:
    keys = get_watched_keys()
    if not keys:
        print("Watchlist is empty.")
        return
    print("Watched keys:")
    for key in keys:
        print(f"  {key}")


def cmd_watch_check(args: argparse.Namespace) -> None:
    """Check whether a key is currently on the watchlist."""
    if is_watched(args.key):
        print(f"{args.key} is watched.")
    else:
        print(f"{args.key} is NOT watched.")


def register_watchlist_commands(subparsers) -> None:
    p_add = subparsers.add_parser("watch-add", help="Add a key to the watchlist")
    p_add.add_argument("key", help="Environment variable key to watch")
    p_add.add_argument("--label", default=None, help="Optional human-readable label")
    p_add.set_defaults(func=cmd_watch_add)

    p_rm = subparsers.add_parser("watch-remove", help="Remove a key from the watchlist")
    p_rm.add_argument("key", help="Environment variable key to unwatch")
    p_rm.set_defaults(func=cmd_watch_remove)

    p_ls = subparsers.add_parser("watch-list", help="List all watched keys")
    p_ls.set_defaults(func=cmd_watch_list)

    p_chk = subparsers.add_parser("watch-check", help="Check if a key is watched")
    p_chk.add_argument("key", help="Environment variable key to check")
    p_chk.set_defaults(func=cmd_watch_check)
