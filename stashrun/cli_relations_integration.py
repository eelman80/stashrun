"""Integration hook for relation commands."""
from stashrun.cli_relations import register_relation_commands


def attach(subparsers) -> None:
    register_relation_commands(subparsers)
