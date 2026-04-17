"""CLI commands for per-key snapshot comments."""
from __future__ import annotations
import argparse
from stashrun.snapshots_comments import (
    set_comment, get_comment, remove_comment, get_all_comments, clear_comments
)


def cmd_comment_set(args: argparse.Namespace) -> None:
    set_comment(args.snapshot, args.key, args.comment)
    print(f"Comment set on '{args.snapshot}[{args.key}]'.")


def cmd_comment_get(args: argparse.Namespace) -> None:
    c = get_comment(args.snapshot, args.key)
    if c is None:
        print(f"No comment for '{args.snapshot}[{args.key}]'.")
    else:
        print(c)


def cmd_comment_remove(args: argparse.Namespace) -> None:
    if remove_comment(args.snapshot, args.key):
        print(f"Comment removed from '{args.snapshot}[{args.key}]'.")
    else:
        print(f"No comment found for '{args.snapshot}[{args.key}]'.")


def cmd_comment_list(args: argparse.Namespace) -> None:
    comments = get_all_comments(args.snapshot)
    if not comments:
        print(f"No comments for snapshot '{args.snapshot}'.")
        return
    for key, text in sorted(comments.items()):
        print(f"  {key}: {text}")


def cmd_comment_clear(args: argparse.Namespace) -> None:
    count = clear_comments(args.snapshot)
    print(f"Cleared {count} comment(s) from '{args.snapshot}'.")


def register_comment_commands(subparsers) -> None:
    p = subparsers.add_parser("comment-set", help="Set a comment on a snapshot key")
    p.add_argument("snapshot"); p.add_argument("key"); p.add_argument("comment")
    p.set_defaults(func=cmd_comment_set)

    p = subparsers.add_parser("comment-get", help="Get the comment for a snapshot key")
    p.add_argument("snapshot"); p.add_argument("key")
    p.set_defaults(func=cmd_comment_get)

    p = subparsers.add_parser("comment-remove", help="Remove a comment from a snapshot key")
    p.add_argument("snapshot"); p.add_argument("key")
    p.set_defaults(func=cmd_comment_remove)

    p = subparsers.add_parser("comment-list", help="List all comments for a snapshot")
    p.add_argument("snapshot")
    p.set_defaults(func=cmd_comment_list)

    p = subparsers.add_parser("comment-clear", help="Clear all comments for a snapshot")
    p.add_argument("snapshot")
    p.set_defaults(func=cmd_comment_clear)
