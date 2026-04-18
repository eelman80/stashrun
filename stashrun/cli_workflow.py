"""CLI commands for snapshot workflows."""
from __future__ import annotations
import argparse
from stashrun.snapshots_workflow import (
    create_workflow, delete_workflow, get_workflow,
    list_workflows, add_step, remove_step, run_workflow,
)


def cmd_workflow_create(args: argparse.Namespace) -> None:
    steps = args.steps or []
    if create_workflow(args.name, steps):
        print(f"Workflow '{args.name}' created with {len(steps)} step(s).")
    else:
        print(f"Workflow '{args.name}' already exists.")


def cmd_workflow_delete(args: argparse.Namespace) -> None:
    if delete_workflow(args.name):
        print(f"Workflow '{args.name}' deleted.")
    else:
        print(f"Workflow '{args.name}' not found.")


def cmd_workflow_show(args: argparse.Namespace) -> None:
    wf = get_workflow(args.name)
    if wf is None:
        print(f"Workflow '{args.name}' not found.")
        return
    steps = wf["steps"]
    if not steps:
        print(f"Workflow '{args.name}' has no steps.")
    else:
        for i, s in enumerate(steps):
            print(f"  {i}: {s}")


def cmd_workflow_list(args: argparse.Namespace) -> None:
    names = list_workflows()
    if not names:
        print("No workflows defined.")
    else:
        for n in names:
            print(n)


def cmd_workflow_add_step(args: argparse.Namespace) -> None:
    if add_step(args.name, args.snapshot):
        print(f"Added '{args.snapshot}' to workflow '{args.name}'.")
    else:
        print(f"Workflow '{args.name}' not found.")


def cmd_workflow_remove_step(args: argparse.Namespace) -> None:
    if remove_step(args.name, args.index):
        print(f"Removed step {args.index} from workflow '{args.name}'.")
    else:
        print(f"Could not remove step {args.index} from workflow '{args.name}'.")


def cmd_workflow_run(args: argparse.Namespace) -> None:
    applied, missing = run_workflow(args.name)
    if missing:
        print(f"Missing snapshots: {', '.join(missing)}")
    print(f"Workflow '{args.name}' completed: {applied} step(s) applied.")


def register_workflow_commands(subparsers) -> None:
    p = subparsers.add_parser("workflow-create", help="Create a workflow")
    p.add_argument("name"); p.add_argument("steps", nargs="*"); p.set_defaults(func=cmd_workflow_create)

    p = subparsers.add_parser("workflow-delete", help="Delete a workflow")
    p.add_argument("name"); p.set_defaults(func=cmd_workflow_delete)

    p = subparsers.add_parser("workflow-show", help="Show workflow steps")
    p.add_argument("name"); p.set_defaults(func=cmd_workflow_show)

    p = subparsers.add_parser("workflow-list", help="List workflows")
    p.set_defaults(func=cmd_workflow_list)

    p = subparsers.add_parser("workflow-add-step", help="Append step to workflow")
    p.add_argument("name"); p.add_argument("snapshot"); p.set_defaults(func=cmd_workflow_add_step)

    p = subparsers.add_parser("workflow-remove-step", help="Remove step by index")
    p.add_argument("name"); p.add_argument("index", type=int); p.set_defaults(func=cmd_workflow_remove_step)

    p = subparsers.add_parser("workflow-run", help="Run a workflow")
    p.add_argument("name"); p.set_defaults(func=cmd_workflow_run)
