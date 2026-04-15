"""CLI commands for managing lifecycle hooks."""

import argparse

from stashrun.hooks import HOOK_EVENTS, get_hook, list_hooks, remove_hook, set_hook


def cmd_hook_set(args: argparse.Namespace) -> None:
    if args.event not in HOOK_EVENTS:
        print(f"Unknown event '{args.event}'. Valid events: {', '.join(HOOK_EVENTS)}")
        return
    set_hook(args.event, args.command)
    print(f"Hook set for '{args.event}': {args.command}")


def cmd_hook_remove(args: argparse.Namespace) -> None:
    if remove_hook(args.event):
        print(f"Hook removed for '{args.event}'.")
    else:
        print(f"No hook registered for '{args.event}'.")


def cmd_hook_show(args: argparse.Namespace) -> None:
    cmd = get_hook(args.event)
    if cmd:
        print(f"{args.event}: {cmd}")
    else:
        print(f"No hook registered for '{args.event}'.")


def cmd_hook_list(args: argparse.Namespace) -> None:
    hooks = list_hooks()
    if not hooks:
        print("No hooks registered.")
        return
    for event, command in hooks.items():
        print(f"  {event}: {command}")


def register_hook_commands(subparsers) -> None:
    hook_p = subparsers.add_parser("hook", help="Manage lifecycle hooks")
    hook_sub = hook_p.add_subparsers(dest="hook_cmd")

    p_set = hook_sub.add_parser("set", help="Register a hook command for an event")
    p_set.add_argument("event", choices=HOOK_EVENTS)
    p_set.add_argument("command", help="Shell command to run")
    p_set.set_defaults(func=cmd_hook_set)

    p_rm = hook_sub.add_parser("remove", help="Remove a hook")
    p_rm.add_argument("event", choices=HOOK_EVENTS)
    p_rm.set_defaults(func=cmd_hook_remove)

    p_show = hook_sub.add_parser("show", help="Show hook for an event")
    p_show.add_argument("event", choices=HOOK_EVENTS)
    p_show.set_defaults(func=cmd_hook_show)

    p_list = hook_sub.add_parser("list", help="List all registered hooks")
    p_list.set_defaults(func=cmd_hook_list)
