"""CLI commands for snapshot attribution management."""

from __future__ import annotations

from argparse import Namespace
from typing import List

from stashrun.snapshots_attribution import (
    add_contributor,
    find_by_author,
    get_attribution,
    list_attributions,
    remove_attribution,
    set_attribution,
)


def cmd_attribution_set(args: Namespace) -> None:
    contributors: List[str] = args.contributors or []
    set_attribution(args.name, args.author, contributors=contributors, source=getattr(args, "source", None))
    print(f"Attribution set for '{args.name}' (author: {args.author}).")


def cmd_attribution_get(args: Namespace) -> None:
    info = get_attribution(args.name)
    if info is None:
        print(f"No attribution found for '{args.name}'.")
        return
    print(f"Author   : {info['author']}")
    print(f"Contributors: {', '.join(info['contributors']) or '—'}")
    print(f"Source   : {info.get('source') or '—'}")


def cmd_attribution_add_contributor(args: Namespace) -> None:
    ok = add_contributor(args.name, args.contributor)
    if ok:
        print(f"Contributor '{args.contributor}' added to '{args.name}'.")
    else:
        print(f"No attribution entry found for '{args.name}'.")


def cmd_attribution_remove(args: Namespace) -> None:
    ok = remove_attribution(args.name)
    if ok:
        print(f"Attribution removed for '{args.name}'.")
    else:
        print(f"No attribution entry found for '{args.name}'.")


def cmd_attribution_list(args: Namespace) -> None:
    entries = list_attributions()
    if not entries:
        print("No attribution entries found.")
        return
    for name, info in sorted(entries.items()):
        contribs = ", ".join(info.get("contributors", [])) or "—"
        print(f"{name}  author={info['author']}  contributors=[{contribs}]")


def cmd_attribution_find(args: Namespace) -> None:
    names = find_by_author(args.author)
    if not names:
        print(f"No snapshots attributed to '{args.author}'.")
        return
    for n in sorted(names):
        print(n)


def register_attribution_commands(subparsers) -> None:
    p = subparsers.add_parser("attribution-set", help="Set attribution for a snapshot")
    p.add_argument("name")
    p.add_argument("author")
    p.add_argument("--contributors", nargs="*")
    p.add_argument("--source")
    p.set_defaults(func=cmd_attribution_set)

    p = subparsers.add_parser("attribution-get", help="Show attribution for a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_attribution_get)

    p = subparsers.add_parser("attribution-add-contributor", help="Add a contributor to a snapshot attribution")
    p.add_argument("name")
    p.add_argument("contributor")
    p.set_defaults(func=cmd_attribution_add_contributor)

    p = subparsers.add_parser("attribution-remove", help="Remove attribution for a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_attribution_remove)

    p = subparsers.add_parser("attribution-list", help="List all attribution entries")
    p.set_defaults(func=cmd_attribution_list)

    p = subparsers.add_parser("attribution-find", help="Find snapshots by author")
    p.add_argument("author")
    p.set_defaults(func=cmd_attribution_find)
