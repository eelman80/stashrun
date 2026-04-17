"""Attach group commands to the main CLI parser."""

from stashrun.cli_groups import register_group_commands


def attach(subparsers):
    register_group_commands(subparsers)
