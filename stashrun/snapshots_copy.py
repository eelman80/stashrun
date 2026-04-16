"""Copy and rename snapshots."""

from stashrun.storage import load_snapshot, save_snapshot, list_snapshots


def copy_snapshot(src_name: str, dst_name: str, overwrite: bool = False) -> bool:
    """Copy a snapshot under a new name. Returns True on success."""
    env = load_snapshot(src_name)
    if env is None:
        return False
    if not overwrite and dst_name in list_snapshots():
        return False
    save_snapshot(dst_name, env)
    return True


def rename_snapshot(src_name: str, dst_name: str, overwrite: bool = False) -> bool:
    """Rename a snapshot. Returns True on success."""
    from stashrun.storage import delete_snapshot
    env = load_snapshot(src_name)
    if env is None:
        return False
    if not overwrite and dst_name in list_snapshots():
        return False
    save_snapshot(dst_name, env)
    delete_snapshot(src_name)
    return True


def snapshot_exists(name: str) -> bool:
    return name in list_snapshots()
