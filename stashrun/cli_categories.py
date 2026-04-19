"""CLI commands for snapshot categories."""

from stashrun.snapshots_categories import (
    set_category, get_category, remove_category,
    list_categories, find_by_category, all_category_names,
)


def cmd_category_set(args):
    set_category(args.name, args.category)
    print(f"Category '{args.category}' assigned to '{args.name}'.")


def cmd_category_get(args):
    cat = get_category(args.name)
    print(f"{args.name}: {cat}")


def cmd_category_remove(args):
    if remove_category(args.name):
        print(f"Category removed from '{args.name}'.")
    else:
        print(f"No category set for '{args.name}'.")


def cmd_category_list(args):
    data = list_categories()
    if not data:
        print("No categories assigned.")
        return
    for name, cat in sorted(data.items()):
        print(f"  {name}: {cat}")


def cmd_category_find(args):
    names = find_by_category(args.category)
    if not names:
        print(f"No snapshots in category '{args.category}'.")
        return
    for n in names:
        print(f"  {n}")


def cmd_category_all(args):
    cats = all_category_names()
    if not cats:
        print("No categories in use.")
        return
    for c in cats:
        print(f"  {c}")


def register_category_commands(subparsers):
    p = subparsers.add_parser("category-set", help="Assign category to snapshot")
    p.add_argument("name"); p.add_argument("category"); p.set_defaults(func=cmd_category_set)

    p = subparsers.add_parser("category-get", help="Get snapshot category")
    p.add_argument("name"); p.set_defaults(func=cmd_category_get)

    p = subparsers.add_parser("category-remove", help="Remove snapshot category")
    p.add_argument("name"); p.set_defaults(func=cmd_category_remove)

    p = subparsers.add_parser("category-list", help="List all category assignments")
    p.set_defaults(func=cmd_category_list)

    p = subparsers.add_parser("category-find", help="Find snapshots by category")
    p.add_argument("category"); p.set_defaults(func=cmd_category_find)

    p = subparsers.add_parser("category-all", help="List all distinct categories")
    p.set_defaults(func=cmd_category_all)
