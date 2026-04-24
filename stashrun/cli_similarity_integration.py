"""Integration hook to attach similarity commands to the main CLI parser."""

from stashrun.cli_similarity import register_similarity_commands


def attach(subparsers):
    """Attach snapshot similarity commands to the given subparsers."""
    register_similarity_commands(subparsers)
