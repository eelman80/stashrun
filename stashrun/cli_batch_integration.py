"""Attach batch commands to the main CLI parser."""

from stashrun.cli_batch import register_batch_commands


def attach(subparsers) -> None:
    """Register batch subcommands onto an existing subparsers group."""
    register_batch_commands(subparsers)
