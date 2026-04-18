"""Integration hook to attach ownership commands to the main CLI."""

from stashrun.cli_ownership import register_ownership_commands


def attach(subparsers):
    register_ownership_commands(subparsers)
