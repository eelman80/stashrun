"""CLI commands for snapshot health reporting."""

from stashrun.snapshots_health import compute_health, health_summary


def cmd_health_show(args):
    report = compute_health(args.name)
    if report is None:
        print(f"Snapshot '{args.name}' not found.")
        return
    print(f"Snapshot : {report['name']}")
    print(f"Score    : {report['score']}/100")
    print(f"Status   : {report['status']}")
    if report["issues"]:
        print("Issues:")
        for issue in report["issues"]:
            print(f"  - {issue}")
    else:
        print("No issues found.")


def cmd_health_summary(args):
    reports = health_summary()
    if not reports:
        print("No snapshots found.")
        return
    print(f"{'Name':<30} {'Score':>6}  Status")
    print("-" * 50)
    for r in reports:
        print(f"{r['name']:<30} {r['score']:>6}  {r['status']}")


def register_health_commands(subparsers):
    p_show = subparsers.add_parser("health", help="Show health report for a snapshot")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_health_show)

    p_summary = subparsers.add_parser("health-summary", help="Health overview of all snapshots")
    p_summary.set_defaults(func=cmd_health_summary)
