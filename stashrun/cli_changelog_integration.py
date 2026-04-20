"""Integration hook to attach changelog commands to the main CLI."""

from stashrun.cli_changelog import register_changelog_commands


def attach(subparsers) -> None:
    """Attach changelog subcommands to the provided subparsers.

    This function serves as the integration entry point between the main
    CLI and the changelog command module. It delegates registration to
    ``register_changelog_commands``, keeping the integration layer thin
    and the changelog command definitions self-contained.

    Args:
        subparsers: The subparsers action object returned by
            ``ArgumentParser.add_subparsers()``, used to register new
            subcommands.
    """
    register_changelog_commands(subparsers)
