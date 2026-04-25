"""Integration hook to attach momentum commands to the main CLI parser."""

from stashrun.cli_momentum import register_momentum_commands


def attach(subparsers) -> None:
    """Attach momentum sub-commands to the provided subparsers."""
    register_momentum_commands(subparsers)
