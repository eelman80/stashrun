"""Integration shim to attach influence commands to the main CLI."""

from stashrun.cli_influence import register_influence_commands


def attach(subparsers) -> None:
    register_influence_commands(subparsers)
