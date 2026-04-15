"""CLI commands for managing env variable templates in stashrun."""

import argparse
import json
import os

from stashrun.templates import (
    apply_template,
    delete_template,
    get_template,
    list_templates,
    save_template,
)


def cmd_template_save(args: argparse.Namespace) -> None:
    """Save a template from a comma-separated list of KEY=default or KEY entries."""
    variables = {}
    for item in args.vars:
        if "=" in item:
            key, _, default = item.partition("=")
            variables[key.strip()] = default.strip()
        else:
            variables[item.strip()] = None
    if save_template(args.name, variables):
        print(f"Template '{args.name}' saved with {len(variables)} variable(s).")


def cmd_template_delete(args: argparse.Namespace) -> None:
    if delete_template(args.name):
        print(f"Template '{args.name}' deleted.")
    else:
        print(f"Template '{args.name}' not found.")


def cmd_template_show(args: argparse.Namespace) -> None:
    template = get_template(args.name)
    if template is None:
        print(f"Template '{args.name}' not found.")
        return
    print(f"Template: {args.name}")
    for key, default in template.items():
        default_str = f" (default: {default})" if default is not None else ""
        print(f"  {key}{default_str}")


def cmd_template_list(args: argparse.Namespace) -> None:
    names = list_templates()
    if not names:
        print("No templates defined.")
    else:
        for name in names:
            print(name)


def cmd_template_apply(args: argparse.Namespace) -> None:
    """Apply a template to the current environment and print the filtered result."""
    env = dict(os.environ)
    result = apply_template(args.name, env)
    if result is None:
        print(f"Template '{args.name}' not found.")
        return
    print(json.dumps(result, indent=2))


def register_template_commands(subparsers) -> None:
    tp = subparsers.add_parser("template", help="Manage env variable templates")
    tp_sub = tp.add_subparsers(dest="template_cmd")

    p_save = tp_sub.add_parser("save", help="Save a template")
    p_save.add_argument("name")
    p_save.add_argument("vars", nargs="+", metavar="KEY[=default]")
    p_save.set_defaults(func=cmd_template_save)

    p_del = tp_sub.add_parser("delete", help="Delete a template")
    p_del.add_argument("name")
    p_del.set_defaults(func=cmd_template_delete)

    p_show = tp_sub.add_parser("show", help="Show a template")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_template_show)

    p_list = tp_sub.add_parser("list", help="List all templates")
    p_list.set_defaults(func=cmd_template_list)

    p_apply = tp_sub.add_parser("apply", help="Apply template to current env")
    p_apply.add_argument("name")
    p_apply.set_defaults(func=cmd_template_apply)
