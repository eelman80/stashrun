"""CLI commands for snapshot alignment."""

from stashrun.snapshots_alignment import compute_alignment, alignment_rank, alignment_summary


def cmd_alignment_show(args) -> None:
    """Show alignment of a snapshot against a template."""
    result = compute_alignment(args.name, args.template)
    if result is None:
        print(f"[alignment] snapshot '{args.name}' or template '{args.template}' not found.")
        return
    print(f"Alignment of '{args.name}' vs template '{args.template}': {result['score']}/100")
    if result["matched"]:
        print(f"  Matched : {', '.join(result['matched'])}")
    if result["missing"]:
        print(f"  Missing : {', '.join(result['missing'])}")
    if result["extra"]:
        print(f"  Extra   : {', '.join(result['extra'])}")


def cmd_alignment_top(args) -> None:
    """List snapshots ranked by alignment to a template."""
    ranked = alignment_rank(args.template, top=getattr(args, "top", 10))
    if not ranked:
        print(f"[alignment] no snapshots found for template '{args.template}'.")
        return
    for name, score in ranked:
        print(f"  {score:>3}/100  {name}")


def cmd_alignment_summary(args) -> None:
    """Print summary statistics for alignment against a template."""
    summary = alignment_summary(args.template)
    print(f"Alignment summary for template '{args.template}':")
    print(f"  Snapshots : {summary['count']}")
    print(f"  Average   : {summary['average']}")
    print(f"  Min       : {summary['min']}")
    print(f"  Max       : {summary['max']}")


def register_alignment_commands(subparsers) -> None:
    p_show = subparsers.add_parser("alignment-show", help="Show alignment score for a snapshot")
    p_show.add_argument("name", help="Snapshot name")
    p_show.add_argument("template", help="Reference template name")
    p_show.set_defaults(func=cmd_alignment_show)

    p_top = subparsers.add_parser("alignment-top", help="Rank snapshots by alignment")
    p_top.add_argument("template", help="Reference template name")
    p_top.add_argument("--top", type=int, default=10, help="Number of results")
    p_top.set_defaults(func=cmd_alignment_top)

    p_sum = subparsers.add_parser("alignment-summary", help="Alignment summary for a template")
    p_sum.add_argument("template", help="Reference template name")
    p_sum.set_defaults(func=cmd_alignment_summary)
