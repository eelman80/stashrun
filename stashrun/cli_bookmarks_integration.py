"""Attach bookmark commands to the main CLI parser."""

from stashrun.cli_bookmarks import register_bookmark_commands


def attach(subparsers):
    register_bookmark_commands(subparsers)
