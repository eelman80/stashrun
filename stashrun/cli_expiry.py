"""CLI commands for snapshot expiry management."""

import argparse
from stashrun.snapshots_expiry import is_expired, list_expired, purge_expired, expiry_status


def cmd_expiry_check(args: argparse.Namespace) -> None:
    """Check and display the expiry status of a named snapshot."""
    try:
        status = expiry_status(args.name)
    except KeyError:
        print(f"Error: snapshot '{args.name}' not found.")
        return
    if not status["has_ttl"]:
        print(f"{args.name}: no TTL set")
        return
    state = "EXPIRED" if status["expired"] else "active"
    print(f"{args.name}: {state} (expires {status['expiry_iso']})")


def cmd_expiry_list(args: argparse.Namespace) -> None:
    """List all snapshots that have passed their expiry time."""
    expired = list_expired()
    if not expired:
        print("No expired snapshots.")
        return
    for name in expired:
        print(name)


def cmd_expiry_purge(args: argparse.Namespace) -> None:
    """Delete all expired snapshots, or preview deletions with --dry-run."""
    purged = purge_expired(dry_run=args.dry_run)
    if not purged:
        print("Nothing to purge.")
        return
    label = "Would purge" if args.dry_run else "Purged"
    for name in purged:
        print(f"{label}: {name}")


def register_expiry_commands(subparsers) -> None:
    """Register all expiry-related subcommands onto the given subparsers object."""
    p_check = subparsers.add_parser("expiry-check", help="Check expiry status of a snapshot")
    p_check.add_argument("name")
    p_check.set_defaults(func=cmd_expiry_check)

    p_list = subparsers.add_parser("expiry-list", help="List all expired snapshots")
    p_list.set_defaults(func=cmd_expiry_list)

    p_purge = subparsers.add_parser("expiry-purge", help="Delete expired snapshots")
    p_purge.add_argument("--dry-run", action="store_true", help="Preview without deleting")
    p_purge.set_defaults(func=cmd_expiry_purge)
