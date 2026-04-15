"""CLI commands for merging snapshots."""

import argparse
from stashrun.snapshots_merge import (
    merge_snapshots,
    merge_conflicts,
    MERGE_STRATEGY_LAST_WINS,
    MERGE_STRATEGY_FIRST_WINS,
    MERGE_STRATEGY_STRICT,
)

STRATEGIES = [
    MERGE_STRATEGY_LAST_WINS,
    MERGE_STRATEGY_FIRST_WINS,
    MERGE_STRATEGY_STRICT,
]


def cmd_merge(args: argparse.Namespace) -> None:
    """Merge two or more snapshots into a new snapshot."""
    try:
        merged = merge_snapshots(
            names=args.sources,
            target_name=args.target,
            strategy=args.strategy,
        )
    except ValueError as exc:
        print(f"[error] Merge conflict (strict mode): {exc}")
        return

    if merged is None:
        print("[error] One or more source snapshots not found.")
        return

    print(
        f"[ok] Merged {args.sources} → '{args.target}' "
        f"({len(merged)} keys, strategy={args.strategy})"
    )


def cmd_merge_conflicts(args: argparse.Namespace) -> None:
    """Show conflicting keys across snapshots without merging."""
    conflicts = merge_conflicts(args.sources)
    if not conflicts:
        print("No conflicts found.")
        return

    print(f"Conflicts across {args.sources}:")
    for key, values in sorted(conflicts.items()):
        print(f"  {key}:")
        for v in values:
            print(f"    - {v!r}")


def register_merge_commands(subparsers) -> None:
    """Register merge sub-commands onto an argparse subparsers object."""
    p_merge = subparsers.add_parser("merge", help="Merge snapshots")
    p_merge.add_argument("sources", nargs="+", metavar="SOURCE",
                         help="Source snapshot names (in merge order)")
    p_merge.add_argument("--into", dest="target", required=True,
                         metavar="TARGET", help="Name of the resulting snapshot")
    p_merge.add_argument("--strategy", choices=STRATEGIES,
                         default=MERGE_STRATEGY_LAST_WINS,
                         help="Conflict resolution strategy")
    p_merge.set_defaults(func=cmd_merge)

    p_conflicts = subparsers.add_parser(
        "merge-conflicts", help="Preview conflicts before merging"
    )
    p_conflicts.add_argument("sources", nargs="+", metavar="SOURCE")
    p_conflicts.set_defaults(func=cmd_merge_conflicts)
