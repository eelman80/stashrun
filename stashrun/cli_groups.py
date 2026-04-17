"""CLI commands for snapshot groups."""

from stashrun.snapshots_groups import (
    create_group, delete_group, add_to_group,
    remove_from_group, get_group, list_groups, find_groups_for_snapshot,
)


def cmd_group_create(args):
    if create_group(args.name):
        print(f"Group '{args.name}' created.")
    else:
        print(f"Group '{args.name}' already exists.")


def cmd_group_delete(args):
    if delete_group(args.name):
        print(f"Group '{args.name}' deleted.")
    else:
        print(f"Group '{args.name}' not found.")


def cmd_group_add(args):
    if add_to_group(args.group, args.snapshot):
        print(f"Added '{args.snapshot}' to group '{args.group}'.")
    else:
        print(f"Group '{args.group}' not found.")


def cmd_group_remove(args):
    if remove_from_group(args.group, args.snapshot):
        print(f"Removed '{args.snapshot}' from group '{args.group}'.")
    else:
        print(f"Entry not found.")


def cmd_group_show(args):
    members = get_group(args.name)
    if members is None:
        print(f"Group '{args.name}' not found.")
        return
    if not members:
        print(f"Group '{args.name}' is empty.")
        return
    for m in members:
        print(m)


def cmd_group_list(args):
    groups = list_groups()
    if not groups:
        print("No groups defined.")
        return
    for g in groups:
        print(g)


def cmd_group_find(args):
    groups = find_groups_for_snapshot(args.snapshot)
    if not groups:
        print(f"'{args.snapshot}' is not in any group.")
        return
    for g in groups:
        print(g)


def register_group_commands(subparsers):
    p = subparsers.add_parser("group-create", help="Create a snapshot group")
    p.add_argument("name")
    p.set_defaults(func=cmd_group_create)

    p = subparsers.add_parser("group-delete", help="Delete a snapshot group")
    p.add_argument("name")
    p.set_defaults(func=cmd_group_delete)

    p = subparsers.add_parser("group-add", help="Add snapshot to group")
    p.add_argument("group")
    p.add_argument("snapshot")
    p.set_defaults(func=cmd_group_add)

    p = subparsers.add_parser("group-remove", help="Remove snapshot from group")
    p.add_argument("group")
    p.add_argument("snapshot")
    p.set_defaults(func=cmd_group_remove)

    p = subparsers.add_parser("group-show", help="Show members of a group")
    p.add_argument("name")
    p.set_defaults(func=cmd_group_show)

    p = subparsers.add_parser("group-list", help="List all groups")
    p.set_defaults(func=cmd_group_list)

    p = subparsers.add_parser("group-find", help="Find groups containing a snapshot")
    p.add_argument("snapshot")
    p.set_defaults(func=cmd_group_find)
