"""Snapshot sentiment tracking — stores a mood/sentiment label per snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir

VALID_SENTIMENTS = {"positive", "neutral", "negative", "mixed"}


def _sentiment_path() -> Path:
    return get_stash_dir() / "sentiments.json"


def _load_sentiments() -> dict:
    p = _sentiment_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_sentiments(data: dict) -> None:
    p = _sentiment_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def set_sentiment(name: str, sentiment: str) -> bool:
    """Set a sentiment label for a snapshot. Returns False if sentiment invalid."""
    if sentiment not in VALID_SENTIMENTS:
        return False
    data = _load_sentiments()
    data[name] = sentiment
    _save_sentiments(data)
    return True


def get_sentiment(name: str, default: str = "neutral") -> str:
    """Return the sentiment for a snapshot, or default if not set."""
    return _load_sentiments().get(name, default)


def remove_sentiment(name: str) -> bool:
    """Remove sentiment for a snapshot. Returns False if not found."""
    data = _load_sentiments()
    if name not in data:
        return False
    del data[name]
    _save_sentiments(data)
    return True


def list_sentiments() -> dict:
    """Return all snapshot sentiment entries."""
    return _load_sentiments()


def find_by_sentiment(sentiment: str) -> list[str]:
    """Return snapshot names with the given sentiment."""
    return [name for name, s in _load_sentiments().items() if s == sentiment]
