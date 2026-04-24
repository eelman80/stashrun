"""CLI commands for snapshot similarity."""

from stashrun.snapshots_similarity import compute_similarity, find_similar, similarity_matrix


def cmd_similarity_compare(args):
    """Compare two snapshots and print similarity metrics."""
    result = compute_similarity(args.name_a, args.name_b)
    if result is None:
        print(f"[error] one or both snapshots not found: {args.name_a!r}, {args.name_b!r}")
        return
    print(f"Similarity: {result['score']}%")
    print(f"  Key overlap:   {result['key_overlap'] * 100:.1f}%")
    print(f"  Value overlap: {result['value_overlap'] * 100:.1f}%")
    print(f"  Shared keys ({len(result['shared_keys'])}): {', '.join(result['shared_keys']) or 'none'}")


def cmd_similarity_find(args):
    """Find snapshots similar to a given one."""
    threshold = getattr(args, "threshold", 50.0)
    results = find_similar(args.name, threshold=threshold)
    if not results:
        print(f"No snapshots similar to {args.name!r} above {threshold}% threshold.")
        return
    print(f"Snapshots similar to {args.name!r}:")
    for r in results:
        print(f"  {r['snapshot_b']:<30} score={r['score']}%")


def cmd_similarity_matrix(args):
    """Print pairwise similarity matrix for given snapshot names."""
    names = args.names
    if len(names) < 2:
        print("[error] provide at least two snapshot names.")
        return
    pairs = similarity_matrix(names)
    if not pairs:
        print("No valid pairs found.")
        return
    print(f"{'Snapshot A':<25} {'Snapshot B':<25} {'Score':>7}")
    print("-" * 60)
    for p in pairs:
        print(f"{p['snapshot_a']:<25} {p['snapshot_b']:<25} {p['score']:>6}%")


def register_similarity_commands(subparsers):
    p_compare = subparsers.add_parser("similarity-compare", help="Compare two snapshots")
    p_compare.add_argument("name_a")
    p_compare.add_argument("name_b")
    p_compare.set_defaults(func=cmd_similarity_compare)

    p_find = subparsers.add_parser("similarity-find", help="Find similar snapshots")
    p_find.add_argument("name")
    p_find.add_argument("--threshold", type=float, default=50.0)
    p_find.set_defaults(func=cmd_similarity_find)

    p_matrix = subparsers.add_parser("similarity-matrix", help="Pairwise similarity matrix")
    p_matrix.add_argument("names", nargs="+")
    p_matrix.set_defaults(func=cmd_similarity_matrix)
