"""CLI commands for snapshot lifecycle management."""

from stashrun.snapshots_lifecycle import (
    set_lifecycle,
    get_lifecycle,
    remove_lifecycle,
    list_by_state,
    lifecycle_summary,
    LIFECYCLE_STATES,
)


def cmd_lifecycle_set(args):
    if set_lifecycle(args.name, args.state):
        print(f"Lifecycle of '{args.name}' set to '{args.state}'.")
    else:
        print(f"Invalid state '{args.state}'. Choose from: {', '.join(sorted(LIFECYCLE_STATES))}")


def cmd_lifecycle_get(args):
    state = get_lifecycle(args.name)
    print(f"{args.name}: {state}")


def cmd_lifecycle_remove(args):
    if remove_lifecycle(args.name):
        print(f"Lifecycle entry for '{args.name}' removed.")
    else:
        print(f"No lifecycle entry found for '{args.name}'.")


def cmd_lifecycle_list(args):
    names = list_by_state(args.state)
    if not names:
        print(f"No snapshots with state '{args.state}'.")
    else:
        for name in names:
            print(name)


def cmd_lifecycle_summary(args):
    summary = lifecycle_summary()
    for state in sorted(summary):
        names = summary[state]
        print(f"{state}: {len(names)} snapshot(s)")
        for name in names:
            print(f"  - {name}")


def register_lifecycle_commands(subparsers):
    p = subparsers.add_parser("lifecycle-set", help="Set lifecycle state of a snapshot")
    p.add_argument("name")
    p.add_argument("state", choices=sorted(LIFECYCLE_STATES))
    p.set_defaults(func=cmd_lifecycle_set)

    p = subparsers.add_parser("lifecycle-get", help="Get lifecycle state of a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_lifecycle_get)

    p = subparsers.add_parser("lifecycle-remove", help="Remove lifecycle entry for a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_lifecycle_remove)

    p = subparsers.add_parser("lifecycle-list", help="List snapshots by lifecycle state")
    p.add_argument("state", choices=sorted(LIFECYCLE_STATES))
    p.set_defaults(func=cmd_lifecycle_list)

    p = subparsers.add_parser("lifecycle-summary", help="Summary of all lifecycle states")
    p.set_defaults(func=cmd_lifecycle_summary)
