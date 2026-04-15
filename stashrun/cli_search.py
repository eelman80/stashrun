"""CLI commands for searching snapshots."""

import argparse
from stashrun.snapshots_search import (
    search_by_name,
    search_by_tag,
    search_by_key,
    search_by_value,
    search_by_key_pattern,
)


def cmd_search(args: argparse.Namespace) -> None:
    """Search snapshots using various criteria."""
    stash_dir = getattr(args, "stash_dir", None)
    results: list[str] = []

    if args.name:
        results = search_by_name(args.name, stash_dir)
    elif args.tag:
        results = search_by_tag(args.tag, stash_dir)
    elif args.key:
        results = search_by_key(args.key, stash_dir)
    elif args.value:
        results = search_by_value(args.value, stash_dir)
    elif args.key_pattern:
        results = search_by_key_pattern(args.key_pattern, stash_dir)
    else:
        print("[error] specify at least one search option (--name, --tag, --key, --value, --key-pattern)")
        return

    if not results:
        print("[search] no snapshots matched.")
    else:
        print(f"[search] {len(results)} snapshot(s) found:")
        for name in results:
            print(f"  {name}")


def register_search_commands(subparsers) -> None:
    """Register the search subcommand."""
    p = subparsers.add_parser("search", help="Search snapshots by name, tag, key, or value")
    p.add_argument("--name", metavar="PATTERN", help="Search by snapshot name substring")
    p.add_argument("--tag", metavar="TAG", help="Search by tag")
    p.add_argument("--key", metavar="KEY", help="Search by exact env var key")
    p.add_argument("--value", metavar="VALUE", help="Search by exact env var value")
    p.add_argument("--key-pattern", metavar="PATTERN", dest="key_pattern",
                   help="Search by env var key substring")
    p.set_defaults(func=cmd_search)
