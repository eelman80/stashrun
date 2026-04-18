"""CLI commands for snapshot mention tracking."""

from stashrun.snapshots_mentions import (
    add_mention, remove_mention, get_mentions, clear_mentions, find_by_mention
)


def cmd_mention_add(args):
    if add_mention(args.name, args.reference):
        print(f"Mention '{args.reference}' added to '{args.name}'.")
    else:
        print(f"Mention '{args.reference}' already exists on '{args.name}'.")


def cmd_mention_remove(args):
    if remove_mention(args.name, args.reference):
        print(f"Mention '{args.reference}' removed from '{args.name}'.")
    else:
        print(f"Mention '{args.reference}' not found on '{args.name}'.")


def cmd_mention_list(args):
    refs = get_mentions(args.name)
    if not refs:
        print(f"No mentions for '{args.name}'.")
    else:
        for r in refs:
            print(r)


def cmd_mention_clear(args):
    if clear_mentions(args.name):
        print(f"All mentions cleared from '{args.name}'.")
    else:
        print(f"No mentions found for '{args.name}'.")


def cmd_mention_find(args):
    names = find_by_mention(args.reference)
    if not names:
        print(f"No snapshots mention '{args.reference}'.")
    else:
        for n in names:
            print(n)


def register_mention_commands(subparsers):
    p = subparsers.add_parser("mention-add", help="Add a mention to a snapshot")
    p.add_argument("name"); p.add_argument("reference"); p.set_defaults(func=cmd_mention_add)

    p = subparsers.add_parser("mention-remove", help="Remove a mention from a snapshot")
    p.add_argument("name"); p.add_argument("reference"); p.set_defaults(func=cmd_mention_remove)

    p = subparsers.add_parser("mention-list", help="List mentions for a snapshot")
    p.add_argument("name"); p.set_defaults(func=cmd_mention_list)

    p = subparsers.add_parser("mention-clear", help="Clear all mentions from a snapshot")
    p.add_argument("name"); p.set_defaults(func=cmd_mention_clear)

    p = subparsers.add_parser("mention-find", help="Find snapshots by mention reference")
    p.add_argument("reference"); p.set_defaults(func=cmd_mention_find)
