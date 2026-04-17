"""CLI commands for snapshot ratings."""

from stashrun.snapshots_ratings import set_rating, get_rating, remove_rating, list_ratings, top_rated


def cmd_rating_set(args):
    name = args.name
    rating = args.rating
    if set_rating(name, rating):
        print(f"Rated '{name}': {rating}/5")
    else:
        print(f"Invalid rating '{rating}'. Must be between 1 and 5.")


def cmd_rating_get(args):
    r = get_rating(args.name)
    if r is None:
        print(f"No rating for '{args.name}'.")
    else:
        print(f"{args.name}: {r}/5")


def cmd_rating_remove(args):
    if remove_rating(args.name):
        print(f"Rating removed for '{args.name}'.")
    else:
        print(f"No rating found for '{args.name}'.")


def cmd_rating_list(args):
    data = list_ratings()
    if not data:
        print("No ratings recorded.")
        return
    for name, r in sorted(data.items()):
        print(f"  {name}: {r}/5")


def cmd_rating_top(args):
    n = getattr(args, "n", 5)
    results = top_rated(n)
    if not results:
        print("No ratings recorded.")
        return
    for name, r in results:
        print(f"  {name}: {r}/5")


def register_rating_commands(subparsers):
    p = subparsers.add_parser("rating", help="Manage snapshot ratings")
    sub = p.add_subparsers(dest="rating_cmd")

    s = sub.add_parser("set", help="Rate a snapshot")
    s.add_argument("name")
    s.add_argument("rating", type=int)
    s.set_defaults(func=cmd_rating_set)

    g = sub.add_parser("get", help="Get rating for a snapshot")
    g.add_argument("name")
    g.set_defaults(func=cmd_rating_get)

    r = sub.add_parser("remove", help="Remove rating")
    r.add_argument("name")
    r.set_defaults(func=cmd_rating_remove)

    sub.add_parser("list", help="List all ratings").set_defaults(func=cmd_rating_list)

    t = sub.add_parser("top", help="Show top-rated snapshots")
    t.add_argument("--n", type=int, default=5)
    t.set_defaults(func=cmd_rating_top)
