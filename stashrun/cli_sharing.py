"""CLI commands for snapshot sharing."""

from stashrun.snapshots_sharing import (
    encode_snapshot,
    import_share_string,
    share_summary,
)


def cmd_share_encode(args):
    """Encode a snapshot as a portable share string."""
    result = encode_snapshot(args.name)
    if result is None:
        print(f"Snapshot '{args.name}' not found.")
    else:
        print(result)


def cmd_share_import(args):
    """Import a share string as a new snapshot."""
    name = import_share_string(args.share_str, getattr(args, "name", None))
    if name is None:
        print("Invalid share string.")
    else:
        print(f"Imported snapshot as '{name}'.")


def cmd_share_inspect(args):
    """Inspect a share string without importing."""
    summary = share_summary(args.share_str)
    if summary is None:
        print("Invalid share string.")
    else:
        print(f"Name: {summary['name']}")
        print(f"Keys: {summary['key_count']}")


def register_sharing_commands(subparsers):
    p_encode = subparsers.add_parser("share-encode", help="Encode snapshot as share string")
    p_encode.add_argument("name")
    p_encode.set_defaults(func=cmd_share_encode)

    p_import = subparsers.add_parser("share-import", help="Import a share string")
    p_import.add_argument("share_str")
    p_import.add_argument("--name", default=None)
    p_import.set_defaults(func=cmd_share_import)

    p_inspect = subparsers.add_parser("share-inspect", help="Inspect a share string")
    p_inspect.add_argument("share_str")
    p_inspect.set_defaults(func=cmd_share_inspect)
