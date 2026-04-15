"""CLI commands for exporting and importing snapshots."""

import argparse
import sys

from stashrun.export import export_snapshot, import_snapshot


def cmd_export(args: argparse.Namespace) -> int:
    """Export a snapshot to a file."""
    fmt = args.format or _infer_format(args.output)
    success = export_snapshot(args.name, args.output, fmt=fmt)
    if not success:
        print(f"[stashrun] Error: snapshot '{args.name}' not found.", file=sys.stderr)
        return 1
    print(f"[stashrun] Exported '{args.name}' to {args.output} ({fmt})")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    """Import a snapshot from a file."""
    fmt = args.format or _infer_format(args.input)
    name = args.name or _stem(args.input)
    success = import_snapshot(name, args.input, fmt=fmt)
    if not success:
        print(
            f"[stashrun] Error: could not import from '{args.input}'.",
            file=sys.stderr,
        )
        return 1
    print(f"[stashrun] Imported snapshot '{name}' from {args.input} ({fmt})")
    return 0


def _infer_format(filepath: str) -> str:
    """Infer format from file extension; default to json."""
    if filepath.endswith(".env") or filepath.endswith(".dotenv"):
        return "dotenv"
    return "json"


def _stem(filepath: str) -> str:
    """Return the filename stem without extension."""
    from pathlib import Path
    return Path(filepath).stem


def register_export_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register export/import subcommands onto an existing subparsers object."""
    # export
    p_export = subparsers.add_parser("export", help="Export a snapshot to a file")
    p_export.add_argument("name", help="Snapshot name to export")
    p_export.add_argument("output", help="Destination file path")
    p_export.add_argument(
        "--format", choices=["json", "dotenv"], default=None,
        help="Export format (default: inferred from extension)"
    )
    p_export.set_defaults(func=cmd_export)

    # import
    p_import = subparsers.add_parser("import", help="Import a snapshot from a file")
    p_import.add_argument("input", help="Source file path")
    p_import.add_argument(
        "--name", default=None,
        help="Snapshot name (default: inferred from filename)"
    )
    p_import.add_argument(
        "--format", choices=["json", "dotenv"], default=None,
        help="Import format (default: inferred from extension)"
    )
    p_import.set_defaults(func=cmd_import)
