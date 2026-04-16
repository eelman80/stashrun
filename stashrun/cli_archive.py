"""CLI commands for archiving and unarchiving snapshots."""

from stashrun.snapshots_archive import (
    archive_snapshot,
    unarchive_snapshot,
    list_archived,
    get_archived,
    purge_archived,
)


def cmd_archive(args) -> None:
    name = args.name
    if archive_snapshot(name):
        print(f"Archived '{name}'.")
    else:
        print(f"Snapshot '{name}' not found.")


def cmd_unarchive(args) -> None:
    name = args.name
    if unarchive_snapshot(name):
        print(f"Restored '{name}' from archive.")
    else:
        print(f"'{name}' not found in archive.")


def cmd_archive_list(args) -> None:
    names = list_archived()
    if not names:
        print("No archived snapshots.")
    else:
        for n in names:
            print(n)


def cmd_archive_show(args) -> None:
    name = args.name
    env = get_archived(name)
    if env is None:
        print(f"'{name}' not found in archive.")
        return
    for k, v in env.items():
        print(f"{k}={v}")


def cmd_archive_purge(args) -> None:
    name = args.name
    if purge_archived(name):
        print(f"Permanently deleted archived snapshot '{name}'.")
    else:
        print(f"'{name}' not found in archive.")


def register_archive_commands(subparsers) -> None:
    p_arch = subparsers.add_parser("archive", help="Archive a snapshot")
    p_arch.add_argument("name")
    p_arch.set_defaults(func=cmd_archive)

    p_unarch = subparsers.add_parser("unarchive", help="Restore snapshot from archive")
    p_unarch.add_argument("name")
    p_unarch.set_defaults(func=cmd_unarchive)

    p_list = subparsers.add_parser("archive-list", help="List archived snapshots")
    p_list.set_defaults(func=cmd_archive_list)

    p_show = subparsers.add_parser("archive-show", help="Show archived snapshot env")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_archive_show)

    p_purge = subparsers.add_parser("archive-purge", help="Permanently delete archived snapshot")
    p_purge.add_argument("name")
    p_purge.set_defaults(func=cmd_archive_purge)
