"""Integration hook to attach trust commands to the main CLI parser."""

from stashrun.cli_trust import register_trust_commands


def attach(subparsers):
    register_trust_commands(subparsers)
