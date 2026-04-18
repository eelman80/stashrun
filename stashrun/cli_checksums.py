from stashrun.snapshots_checksums import (
    get_checksum,
    store_checksum,
    remove_checksum,
    verify_checksum,
    list_checksums,
)
from stashrun.snapshot import get_snapshot


def cmd_checksum_show(args):
    checksum = get_checksum(args.name)
    if checksum is None:
        print(f"No checksum stored for '{args.name}'.")
    else:
        print(f"{args.name}: {checksum}")


def cmd_checksum_update(args):
    snap = get_snapshot(args.name)
    if snap is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    checksum = store_checksum(args.name, snap)
    print(f"Stored checksum for '{args.name}': {checksum}")


def cmd_checksum_verify(args):
    snap = get_snapshot(args.name)
    if snap is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    result = verify_checksum(args.name, snap)
    if result is None:
        print(f"No checksum on record for '{args.name}'.")
    elif result:
        print(f"OK: '{args.name}' matches stored checksum.")
    else:
        print(f"MISMATCH: '{args.name}' does not match stored checksum.")


def cmd_checksum_remove(args):
    removed = remove_checksum(args.name)
    if removed:
        print(f"Removed checksum for '{args.name}'.")
    else:
        print(f"No checksum found for '{args.name}'.")


def cmd_checksum_list(args):
    data = list_checksums()
    if not data:
        print("No checksums stored.")
        return
    for name, checksum in sorted(data.items()):
        print(f"{name}: {checksum}")


def register_checksum_commands(subparsers):
    p = subparsers.add_parser("checksum-show", help="Show stored checksum")
    p.add_argument("name")
    p.set_defaults(func=cmd_checksum_show)

    p = subparsers.add_parser("checksum-update", help="Compute and store checksum")
    p.add_argument("name")
    p.set_defaults(func=cmd_checksum_update)

    p = subparsers.add_parser("checksum-verify", help="Verify snapshot integrity")
    p.add_argument("name")
    p.set_defaults(func=cmd_checksum_verify)

    p = subparsers.add_parser("checksum-remove", help="Remove stored checksum")
    p.add_argument("name")
    p.set_defaults(func=cmd_checksum_remove)

    p = subparsers.add_parser("checksum-list", help="List all stored checksums")
    p.set_defaults(func=cmd_checksum_list)
