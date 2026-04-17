"""CLI commands for managing stashrun encryption keys."""

import argparse
from stashrun.encryption import generate_key, get_key, save_key_to_file, KEY_ENV_VAR


def cmd_keygen(args: argparse.Namespace) -> None:
    """Generate a new encryption key."""
    key = generate_key()
    if args.save:
        path = save_key_to_file(key)
        print(f"Key saved to {path}")
    else:
        print(f"Generated key (set as {KEY_ENV_VAR} or use --save to persist):")
        print(key)


def cmd_key_status(args: argparse.Namespace) -> None:
    """Show whether an encryption key is currently configured."""
    import os
    if os.environ.get(KEY_ENV_VAR):
        print(f"Encryption key loaded from environment variable {KEY_ENV_VAR}.")
    else:
        key = get_key()
        if key:
            print("Encryption key loaded from key file.")
        else:
            print("No encryption key configured. Snapshots will not be encrypted.")


def cmd_key_clear(args: argparse.Namespace) -> None:
    """Remove the saved encryption key file."""
    import os
    from pathlib import Path
    key_file = Path.home() / ".stashrun_key"
    if key_file.exists():
        key_file.unlink()
        print(f"Encryption key file removed: {key_file}")
    else:
        print("No key file found. Nothing to remove.")


def register_encryption_commands(subparsers: argparse._SubParsersAction) -> None:
    keygen_parser = subparsers.add_parser("keygen", help="Generate a new encryption key")
    keygen_parser.add_argument(
        "--save", action="store_true", help="Save key to ~/.stashrun_key"
    )
    keygen_parser.set_defaults(func=cmd_keygen)

    status_parser = subparsers.add_parser("key-status", help="Show encryption key status")
    status_parser.set_defaults(func=cmd_key_status)

    clear_parser = subparsers.add_parser("key-clear", help="Remove the saved encryption key file")
    clear_parser.set_defaults(func=cmd_key_clear)
