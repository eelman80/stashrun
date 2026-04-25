"""CLI commands for snapshot coherence scoring."""

from __future__ import annotations

import argparse

from stashrun.snapshots_coherence import coherence_rank, coherence_summary, compute_coherence


def cmd_coherence_show(args: argparse.Namespace) -> None:
    report = compute_coherence(args.name)
    if report is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Coherence score for '{args.name}': {report['score']}/100")
    if report["issues"]:
        print("Issues:")
        for issue in report["issues"]:
            print(f"  - {issue}")
    else:
        print("No issues detected.")


def cmd_coherence_top(args: argparse.Namespace) -> None:
    ranked = coherence_rank()
    limit = getattr(args, "limit", 10)
    if not ranked:
        print("No snapshots found.")
        return
    for entry in ranked[:limit]:
        issues = len(entry["issues"])
        print(f"{entry['name']:<30} score={entry['score']:>3}  issues={issues}")


def cmd_coherence_summary(args: argparse.Namespace) -> None:
    summary = coherence_summary()
    if summary["count"] == 0:
        print("No snapshots to summarise.")
        return
    print(f"Snapshots : {summary['count']}")
    print(f"Average   : {summary['average']}")
    print(f"Perfect   : {summary['perfect']}")
    print(f"Degraded  : {summary['degraded']}")


def register_coherence_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_show = subparsers.add_parser("coherence-show", help="Show coherence score for a snapshot")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_coherence_show)

    p_top = subparsers.add_parser("coherence-top", help="Rank snapshots by coherence score")
    p_top.add_argument("--limit", type=int, default=10)
    p_top.set_defaults(func=cmd_coherence_top)

    p_sum = subparsers.add_parser("coherence-summary", help="Summarise coherence across all snapshots")
    p_sum.set_defaults(func=cmd_coherence_summary)
