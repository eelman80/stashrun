"""CLI commands for managing snapshot schedules."""

from __future__ import annotations

from stashrun.scheduling import (
    find_schedules_for_snapshot,
    get_schedule,
    list_schedules,
    remove_schedule,
    set_schedule,
)


def cmd_schedule_set(args) -> None:
    """stashrun schedule-set <name> <snapshot> <cron>"""
    entry = set_schedule(args.name, args.snapshot, args.cron)
    print(f"Schedule '{args.name}' set: snapshot='{entry['snapshot']}' cron='{entry['cron']}'")


def cmd_schedule_remove(args) -> None:
    """stashrun schedule-remove <name>"""
    if remove_schedule(args.name):
        print(f"Schedule '{args.name}' removed.")
    else:
        print(f"Schedule '{args.name}' not found.")


def cmd_schedule_show(args) -> None:
    """stashrun schedule-show <name>"""
    entry = get_schedule(args.name)
    if entry is None:
        print(f"Schedule '{args.name}' not found.")
        return
    print(f"name:     {args.name}")
    print(f"snapshot: {entry['snapshot']}")
    print(f"cron:     {entry['cron']}")


def cmd_schedule_list(args) -> None:  # noqa: ARG001
    """stashrun schedule-list"""
    schedules = list_schedules()
    if not schedules:
        print("No schedules defined.")
        return
    for name, entry in schedules.items():
        print(f"{name}  ->  {entry['snapshot']}  [{entry['cron']}]")


def cmd_schedule_find(args) -> None:
    """stashrun schedule-find <snapshot>"""
    names = find_schedules_for_snapshot(args.snapshot)
    if not names:
        print(f"No schedules reference snapshot '{args.snapshot}'.")
        return
    for name in names:
        print(name)


def register_schedule_commands(subparsers) -> None:
    p_set = subparsers.add_parser("schedule-set", help="Create or update a schedule")
    p_set.add_argument("name")
    p_set.add_argument("snapshot")
    p_set.add_argument("cron")
    p_set.set_defaults(func=cmd_schedule_set)

    p_rm = subparsers.add_parser("schedule-remove", help="Remove a schedule")
    p_rm.add_argument("name")
    p_rm.set_defaults(func=cmd_schedule_remove)

    p_show = subparsers.add_parser("schedule-show", help="Show a schedule")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_schedule_show)

    p_list = subparsers.add_parser("schedule-list", help="List all schedules")
    p_list.set_defaults(func=cmd_schedule_list)

    p_find = subparsers.add_parser("schedule-find", help="Find schedules by snapshot name")
    p_find.add_argument("snapshot")
    p_find.set_defaults(func=cmd_schedule_find)
