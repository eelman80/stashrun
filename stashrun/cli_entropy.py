"""CLI commands for snapshot entropy analysis."""

from __future__ import annotations

from stashrun.snapshots_entropy import compute_entropy, entropy_rank, entropy_summary


def cmd_entropy_show(args) -> None:
    """Show entropy report for a single snapshot."""
    report = compute_entropy(args.name)
    if report is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Entropy report for '{args.name}':")
    print(f"  Mean entropy : {report['mean_entropy']} bits")
    print(f"  Max entropy  : {report['max_entropy']} bits")
    print(f"  Score        : {report['score']}/100")
    if report["high_entropy_keys"]:
        print(f"  High-entropy keys: {', '.join(report['high_entropy_keys'])}")
    else:
        print("  High-entropy keys: none")


def cmd_entropy_top(args) -> None:
    """List snapshots ranked by entropy score."""
    limit = getattr(args, "limit", 10)
    ranked = entropy_rank()[:limit]
    if not ranked:
        print("No snapshots found.")
        return
    for name, score in ranked:
        print(f"  {score:>3}/100  {name}")


def cmd_entropy_summary(args) -> None:  # noqa: ARG001
    """Print aggregate entropy summary."""
    summary = entropy_summary()
    print(f"Total snapshots : {summary['total']}")
    print(f"Average score   : {summary['average_score']}/100")
    if summary["top"]:
        print(f"Most entropic   : {summary['top']}")


def register_entropy_commands(subparsers) -> None:
    """Attach entropy sub-commands to an argparse subparsers group."""
    p_show = subparsers.add_parser("entropy-show", help="Show entropy report for a snapshot")
    p_show.add_argument("name", help="Snapshot name")
    p_show.set_defaults(func=cmd_entropy_show)

    p_top = subparsers.add_parser("entropy-top", help="Rank snapshots by entropy score")
    p_top.add_argument("--limit", type=int, default=10, help="Max results")
    p_top.set_defaults(func=cmd_entropy_top)

    p_sum = subparsers.add_parser("entropy-summary", help="Aggregate entropy statistics")
    p_sum.set_defaults(func=cmd_entropy_summary)
