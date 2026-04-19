"""CLI commands for snapshot maturity management."""

from stashrun.snapshots_maturity import (
    set_maturity, get_maturity, remove_maturity,
    list_maturity, find_by_maturity, VALID_LEVELS
)


def cmd_maturity_set(args):
    if set_maturity(args.name, args.level):
        print(f"Maturity of '{args.name}' set to '{args.level}'.")
    else:
        print(f"Invalid level '{args.level}'. Choose from: {', '.join(sorted(VALID_LEVELS))}")


def cmd_maturity_get(args):
    level = get_maturity(args.name)
    print(f"{args.name}: {level}")


def cmd_maturity_remove(args):
    if remove_maturity(args.name):
        print(f"Maturity entry for '{args.name}' removed.")
    else:
        print(f"No maturity entry found for '{args.name}'.")


def cmd_maturity_list(args):
    data = list_maturity()
    if not data:
        print("No maturity entries.")
    else:
        for name, level in sorted(data.items()):
            print(f"  {name}: {level}")


def cmd_maturity_find(args):
    results = find_by_maturity(args.level)
    if not results:
        print(f"No snapshots with maturity '{args.level}'.")
    else:
        for name in sorted(results):
            print(f"  {name}")


def register_maturity_commands(subparsers):
    p = subparsers.add_parser("maturity-set", help="Set maturity level of a snapshot")
    p.add_argument("name")
    p.add_argument("level", choices=sorted(VALID_LEVELS))
    p.set_defaults(func=cmd_maturity_set)

    p = subparsers.add_parser("maturity-get", help="Get maturity level of a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_maturity_get)

    p = subparsers.add_parser("maturity-remove", help="Remove maturity entry")
    p.add_argument("name")
    p.set_defaults(func=cmd_maturity_remove)

    p = subparsers.add_parser("maturity-list", help="List all maturity entries")
    p.set_defaults(func=cmd_maturity_list)

    p = subparsers.add_parser("maturity-find", help="Find snapshots by maturity level")
    p.add_argument("level", choices=sorted(VALID_LEVELS))
    p.set_defaults(func=cmd_maturity_find)
