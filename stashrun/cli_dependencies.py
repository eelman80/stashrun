"""CLI commands for snapshot dependency management."""

from stashrun.snapshots_dependencies import (
    add_dependency, remove_dependency, get_dependencies,
    get_dependents, clear_dependencies, all_dependencies,
)


def cmd_dep_add(args):
    if add_dependency(args.name, args.requires):
        print(f"Added dependency: {args.name} -> {args.requires}")
    else:
        print(f"Dependency already exists or invalid.")


def cmd_dep_remove(args):
    if remove_dependency(args.name, args.requires):
        print(f"Removed dependency: {args.name} -> {args.requires}")
    else:
        print(f"Dependency not found.")


def cmd_dep_show(args):
    deps = get_dependencies(args.name)
    if not deps:
        print(f"{args.name} has no dependencies.")
    else:
        print(f"Dependencies of {args.name}:")
        for d in deps:
            print(f"  {d}")


def cmd_dep_dependents(args):
    dependents = get_dependents(args.name)
    if not dependents:
        print(f"No snapshots depend on {args.name}.")
    else:
        print(f"Snapshots depending on {args.name}:")
        for d in dependents:
            print(f"  {d}")


def cmd_dep_clear(args):
    if clear_dependencies(args.name):
        print(f"Cleared all dependencies for {args.name}.")
    else:
        print(f"No dependencies found for {args.name}.")


def cmd_dep_list(args):
    data = all_dependencies()
    if not data:
        print("No dependencies recorded.")
    else:
        for name, deps in data.items():
            print(f"{name}: {', '.join(deps)}")


def register_dependency_commands(subparsers):
    p = subparsers.add_parser("dep-add", help="Add a snapshot dependency")
    p.add_argument("name"); p.add_argument("requires"); p.set_defaults(func=cmd_dep_add)

    p = subparsers.add_parser("dep-remove", help="Remove a snapshot dependency")
    p.add_argument("name"); p.add_argument("requires"); p.set_defaults(func=cmd_dep_remove)

    p = subparsers.add_parser("dep-show", help="Show dependencies of a snapshot")
    p.add_argument("name"); p.set_defaults(func=cmd_dep_show)

    p = subparsers.add_parser("dep-dependents", help="Show snapshots depending on a snapshot")
    p.add_argument("name"); p.set_defaults(func=cmd_dep_dependents)

    p = subparsers.add_parser("dep-clear", help="Clear all dependencies for a snapshot")
    p.add_argument("name"); p.set_defaults(func=cmd_dep_clear)

    p = subparsers.add_parser("dep-list", help="List all recorded dependencies")
    p.set_defaults(func=cmd_dep_list)
