"""CLI commands for snapshot permission management."""

from stashrun.snapshots_permissions import (
    set_permission, get_permissions, has_permission,
    reset_permissions, list_restricted, VALID_PERMISSIONS
)


def cmd_permission_set(args):
    flag = args.allowed.lower() not in ("false", "0", "no", "deny")
    ok = set_permission(args.name, args.permission, flag)
    if not ok:
        print(f"Invalid permission '{args.permission}'. Valid: {', '.join(sorted(VALID_PERMISSIONS))}")
    else:
        state = "granted" if flag else "denied"
        print(f"Permission '{args.permission}' {state} for '{args.name}'.")


def cmd_permission_show(args):
    perms = get_permissions(args.name)
    print(f"Permissions for '{args.name}':")
    for p, v in sorted(perms.items()):
        print(f"  {p}: {'allow' if v else 'deny'}")


def cmd_permission_check(args):
    result = has_permission(args.name, args.permission)
    if args.permission not in VALID_PERMISSIONS:
        print(f"Unknown permission '{args.permission}'.")
        return
    print(f"'{args.name}' {args.permission}: {'allow' if result else 'deny'}")


def cmd_permission_reset(args):
    ok = reset_permissions(args.name)
    if ok:
        print(f"Permissions reset for '{args.name}'.")
    else:
        print(f"No custom permissions found for '{args.name}'.")


def cmd_permission_list_restricted(args):
    names = list_restricted(args.permission)
    if args.permission not in VALID_PERMISSIONS:
        print(f"Unknown permission '{args.permission}'.")
        return
    if not names:
        print(f"No snapshots restricted from '{args.permission}'.")
    else:
        for n in names:
            print(n)


def register_permission_commands(subparsers):
    p = subparsers.add_parser("permission", help="Manage snapshot permissions")
    sub = p.add_subparsers(dest="perm_cmd")

    s = sub.add_parser("set"); s.add_argument("name"); s.add_argument("permission"); s.add_argument("allowed"); s.set_defaults(func=cmd_permission_set)
    s = sub.add_parser("show"); s.add_argument("name"); s.set_defaults(func=cmd_permission_show)
    s = sub.add_parser("check"); s.add_argument("name"); s.add_argument("permission"); s.set_defaults(func=cmd_permission_check)
    s = sub.add_parser("reset"); s.add_argument("name"); s.set_defaults(func=cmd_permission_reset)
    s = sub.add_parser("restricted"); s.add_argument("permission"); s.set_defaults(func=cmd_permission_list_restricted)
