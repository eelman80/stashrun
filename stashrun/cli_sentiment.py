"""CLI commands for snapshot sentiment management."""

from __future__ import annotations

import argparse

from stashrun.snapshots_sentiment import (
    set_sentiment,
    get_sentiment,
    remove_sentiment,
    list_sentiments,
    find_by_sentiment,
    VALID_SENTIMENTS,
)


def cmd_sentiment_set(args: argparse.Namespace) -> None:
    ok = set_sentiment(args.name, args.sentiment)
    if ok:
        print(f"Sentiment '{args.sentiment}' set for '{args.name}'.")
    else:
        print(f"Invalid sentiment '{args.sentiment}'. Choose from: {', '.join(sorted(VALID_SENTIMENTS))}.")


def cmd_sentiment_get(args: argparse.Namespace) -> None:
    s = get_sentiment(args.name)
    print(f"{args.name}: {s}")


def cmd_sentiment_remove(args: argparse.Namespace) -> None:
    ok = remove_sentiment(args.name)
    if ok:
        print(f"Sentiment removed for '{args.name}'.")
    else:
        print(f"No sentiment found for '{args.name}'.")


def cmd_sentiment_list(args: argparse.Namespace) -> None:
    data = list_sentiments()
    if not data:
        print("No sentiments recorded.")
        return
    for name, sentiment in sorted(data.items()):
        print(f"  {name}: {sentiment}")


def cmd_sentiment_find(args: argparse.Namespace) -> None:
    names = find_by_sentiment(args.sentiment)
    if not names:
        print(f"No snapshots with sentiment '{args.sentiment}'.")
        return
    for n in sorted(names):
        print(f"  {n}")


def register_sentiment_commands(subparsers) -> None:
    p = subparsers.add_parser("sentiment-set", help="Set sentiment for a snapshot")
    p.add_argument("name")
    p.add_argument("sentiment")
    p.set_defaults(func=cmd_sentiment_set)

    p = subparsers.add_parser("sentiment-get", help="Get sentiment of a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_sentiment_get)

    p = subparsers.add_parser("sentiment-remove", help="Remove sentiment from a snapshot")
    p.add_argument("name")
    p.set_defaults(func=cmd_sentiment_remove)

    p = subparsers.add_parser("sentiment-list", help="List all snapshot sentiments")
    p.set_defaults(func=cmd_sentiment_list)

    p = subparsers.add_parser("sentiment-find", help="Find snapshots by sentiment")
    p.add_argument("sentiment")
    p.set_defaults(func=cmd_sentiment_find)
