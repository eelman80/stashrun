"""CLI commands for snapshot relations."""
from __future__ import annotations
import argparse
from stashrun.snapshots_relations import (
    add_relation, remove_relation, get_relations,
    find_related, clear_relations, RELATION_TYPES
)


def cmd_relation_add(args: argparse.Namespace) -> None:
    ok = add_relation(args.source, args.target, args.relation)
    if ok:
        print(f"Linked '{args.source}' --[{args.relation}]--> '{args.target}'")
    else:
        print(f"Failed: invalid relation, self-link, or already exists.")


def cmd_relation_remove(args: argparse.Namespace) -> None:
    ok = remove_relation(args.source, args.target, args.relation)
    if ok:
        print(f"Removed relation [{args.relation}] from '{args.source}' to '{args.target}'")
    else:
        print(f"Relation not found.")


def cmd_relation_show(args: argparse.Namespace) -> None:
    rels = get_relations(args.name)
    if not rels:
        print(f"No relations for '{args.name}'.")
        return
    for rel_type, targets in rels.items():
        for t in targets:
            print(f"  [{rel_type}] -> {t}")


def cmd_relation_find(args: argparse.Namespace) -> None:
    targets = find_related(args.name, args.relation)
    if not targets:
        print(f"No '{args.relation}' relations for '{args.name}'.")
        return
    for t in targets:
        print(f"  {t}")


def cmd_relation_clear(args: argparse.Namespace) -> None:
    ok = clear_relations(args.name)
    if ok:
        print(f"Cleared all relations for '{args.name}'.")
    else:
        print(f"No relations found for '{args.name}'.")


def register_relation_commands(subparsers) -> None:
    p = subparsers.add_parser("relation-add", help="Add a relation between snapshots")
    p.add_argument("source"); p.add_argument("target")
    p.add_argument("relation", choices=list(RELATION_TYPES))
    p.set_defaults(func=cmd_relation_add)

    p = subparsers.add_parser("relation-remove", help="Remove a relation")
    p.add_argument("source"); p.add_argument("target")
    p.add_argument("relation", choices=list(RELATION_TYPES))
    p.set_defaults(func=cmd_relation_remove)

    p = subparsers.add_parser("relation-show", help="Show all relations for a snapshot")
    p.add_argument("name"); p.set_defaults(func=cmd_relation_show)

    p = subparsers.add_parser("relation-find", help="Find related snapshots by type")
    p.add_argument("name"); p.add_argument("relation", choices=list(RELATION_TYPES))
    p.set_defaults(func=cmd_relation_find)

    p = subparsers.add_parser("relation-clear", help="Clear all relations for a snapshot")
    p.add_argument("name"); p.set_defaults(func=cmd_relation_clear)
