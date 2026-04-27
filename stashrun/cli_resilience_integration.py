"""Attach resilience commands to the main CLI parser."""

from stashrun.cli_resilience import register_resilience_commands


def attach(subparsers) -> None:
    register_resilience_commands(subparsers)
