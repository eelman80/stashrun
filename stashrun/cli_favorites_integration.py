"""Attach favorite commands to the main CLI parser."""

from stashrun.cli_favorites import register_favorite_commands


def attach(subparsers):
    register_favorite_commands(subparsers)
