"""Integration hook to attach changelog commands to the main CLI."""

from stashrun.cli_changelog import register_changelog_commands


def attach(subparsers) -> None:
    register_changelog_commands(subparsers)
