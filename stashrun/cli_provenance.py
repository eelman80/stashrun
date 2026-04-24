"""CLI commands for snapshot provenance management."""

import argparse

from stashrun.snapshots_provenance import (
    set_provenance,
    get_provenance,
    remove_provenance,
    list_provenance,
    find_by_origin,
    find_by_method,
)


def cmd_provenance_set(args: argparse.Namespace) -> None:
    entry = set_provenance(
        name=args.name,
        origin=args.origin,
        method=args.method or "manual",
        source_context=args.source_context,
        created_by=args.created_by,
    )
    print(f"Provenance set for '{args.name}':")
    for k, v in entry.items():
        if v is not None:
            print(f"  {k}: {v}")


def cmd_provenance_get(args: argparse.Namespace) -> None:
    entry = get_provenance(args.name)
    if entry is None:
        print(f"No provenance record for '{args.name}'.")
        return
    print(f"Provenance for '{args.name}':")
    for k, v in entry.items():
        print(f"  {k}: {v if v is not None else '(unset)'}")


def cmd_provenance_remove(args: argparse.Namespace) -> None:
    if remove_provenance(args.name):
        print(f"Provenance removed for '{args.name}'.")
    else:
        print(f"No provenance record found for '{args.name}'.")


def cmd_provenance_list(args: argparse.Namespace) -> None:
    data = list_provenance()
    if not data:
        print("No provenance records.")
        return
    for name, entry in data.items():
        origin = entry.get("origin", "?")
        method = entry.get("method", "?")
        print(f"  {name}  origin={origin}  method={method}")


def cmd_provenance_find(args: argparse.Namespace) -> None:
    if args.origin:
        results = find_by_origin(args.origin)
        label = f"origin containing '{args.origin}'"
    elif args.method:
        results = find_by_method(args.method)
        label = f"method='{args.method}'"
    else:
        print("Specify --origin or --method to search.")
        return
    if not results:
        print(f"No snapshots found with {label}.")
    else:
        print(f"Snapshots with {label}:")
        for name in results:
            print(f"  {name}")


def register_provenance_commands(subparsers) -> None:
    p = subparsers.add_parser("provenance-set", help="Set provenance for a snapshot")
    p.add_argument("name")
    p.add_argument("origin")
    p.add_argument("--method", default="manual")
    p.add_argument("--source-context", dest="source_context")
    p.add_argument("--created-by", dest="created_by")
    p.set_defaults(func=cmd_provenance_set)

    p = subparsers.add_parser("provenance-get", help="Show provenance for a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_provenance_get)

    p = subparsers.add_parser("provenance-remove", help="Remove provenance record")
    p.add_argument("name")
    p.set_defaults(func=cmd_provenance_remove)

    p = subparsers.add_parser("provenance-list", help="List all provenance records")
    p.set_defaults(func=cmd_provenance_list)

    p = subparsers.add_parser("provenance-find", help="Find snapshots by provenance")
    p.add_argument("--origin")
    p.add_argument("--method")
    p.set_defaults(func=cmd_provenance_find)
