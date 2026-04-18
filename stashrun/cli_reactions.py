"""CLI commands for snapshot reactions."""
from stashrun.snapshots_reactions import (
    add_reaction, remove_reaction, get_reactions,
    clear_reactions, list_all_reactions, VALID_REACTIONS
)


def cmd_reaction_add(args):
    if add_reaction(args.name, args.reaction):
        print(f"Reaction {args.reaction} added to '{args.name}'.")
    else:
        print(f"Invalid reaction '{args.reaction}'. Valid: {' '.join(sorted(VALID_REACTIONS))}")


def cmd_reaction_remove(args):
    if remove_reaction(args.name, args.reaction):
        print(f"Reaction {args.reaction} removed from '{args.name}'.")
    else:
        print(f"Reaction {args.reaction} not found on '{args.name}'.")


def cmd_reaction_list(args):
    reactions = get_reactions(args.name)
    if not reactions:
        print(f"No reactions for '{args.name}'.")
    else:
        print(f"{args.name}: {' '.join(reactions)}")


def cmd_reaction_clear(args):
    if clear_reactions(args.name):
        print(f"All reactions cleared from '{args.name}'.")
    else:
        print(f"No reactions found for '{args.name}'.")


def cmd_reaction_all(args):
    data = list_all_reactions()
    if not data:
        print("No reactions recorded.")
    else:
        for name, reactions in data.items():
            print(f"{name}: {' '.join(reactions)}")


def register_reaction_commands(subparsers):
    p = subparsers.add_parser("reaction", help="Manage snapshot reactions")
    sub = p.add_subparsers(dest="reaction_cmd")

    a = sub.add_parser("add", help="Add a reaction")
    a.add_argument("name")
    a.add_argument("reaction")
    a.set_defaults(func=cmd_reaction_add)

    r = sub.add_parser("remove", help="Remove a reaction")
    r.add_argument("name")
    r.add_argument("reaction")
    r.set_defaults(func=cmd_reaction_remove)

    ls = sub.add_parser("list", help="List reactions for a snapshot")
    ls.add_argument("name")
    ls.set_defaults(func=cmd_reaction_list)

    c = sub.add_parser("clear", help="Clear all reactions for a snapshot")
    c.add_argument("name")
    c.set_defaults(func=cmd_reaction_clear)

    al = sub.add_parser("all", help="Show all reactions")
    al.set_defaults(func=cmd_reaction_all)
