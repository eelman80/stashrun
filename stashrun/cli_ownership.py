"""CLI commands for snapshot ownership management."""

from stashrun.snapshots_ownership import (
    set_owner,
    get_owner,
    remove_owner,
    list_owned_by,
    list_all_owners,
)


def cmd_owner_set(args):
    set_owner(args.name, args.owner)
    print(f"Owner of '{args.name}' set to '{args.owner}'.")


def cmd_owner_get(args):
    owner = get_owner(args.name)
    if owner:
        print(f"{args.name}: {owner}")
    else:
        print(f"No owner set for '{args.name}'.")


def cmd_owner_remove(args):
    if remove_owner(args.name):
        print(f"Ownership record removed for '{args.name}'.")
    else:
        print(f"No ownership record found for '{args.name}'.")


def cmd_owner_list(args):
    if args.owner:
        names = list_owned_by(args.owner)
        if names:
            for n in names:
                print(n)
        else:
            print(f"No snapshots owned by '{args.owner}'.")
    else:
        owners = list_all_owners()
        if owners:
            for name, owner in owners.items():
                print(f"{name}: {owner}")
        else:
            print("No ownership records found.")


def register_ownership_commands(subparsers):
    p_set = subparsers.add_parser("owner-set", help="Set owner of a snapshot")
    p_set.add_argument("name")
    p_set.add_argument("owner")
    p_set.set_defaults(func=cmd_owner_set)

    p_get = subparsers.add_parser("owner-get", help="Get owner of a snapshot")
    p_get.add_argument("name")
    p_get.set_defaults(func=cmd_owner_get)

    p_rm = subparsers.add_parser("owner-remove", help="Remove ownership of a snapshot")
    p_rm.add_argument("name")
    p_rm.set_defaults(func=cmd_owner_remove)

    p_ls = subparsers.add_parser("owner-list", help="List snapshot ownership")
    p_ls.add_argument("--owner", default=None, help="Filter by owner")
    p_ls.set_defaults(func=cmd_owner_list)
