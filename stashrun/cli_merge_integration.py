"""Integration helpers: wire merge commands into the main CLI parser.

This module is intentionally thin — it delegates to cli_merge and is
imported by the main entry-point so that merge sub-commands appear
alongside the rest of the stashrun commands.
"""

from stashrun.cli_merge import register_merge_commands  # noqa: F401


def attach(subparsers) -> None:
    """Attach merge-related sub-commands to *subparsers*.

    Usage in the main CLI module::

        from stashrun.cli_merge_integration import attach as attach_merge
        attach_merge(subparsers)
    """
    register_merge_commands(subparsers)
