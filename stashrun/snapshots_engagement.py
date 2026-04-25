"""Engagement scoring for snapshots based on interactions."""

from stashrun.snapshots_reactions import get_reactions
from stashrun.snapshots_comments import get_comment
from stashrun.snapshots_mentions import get_mentions
from stashrun.snapshots_subscribers import get_subscribers
from stashrun.snapshots_endorsements import get_endorsements
from stashrun.snapshot import get_snapshot
from stashrun.storage import list_snapshots


def compute_engagement(name: str) -> dict | None:
    """Compute an engagement score for a snapshot.

    Returns a dict with component scores and a total, or None if the
    snapshot does not exist.
    """
    if get_snapshot(name) is None:
        return None

    reactions = get_reactions(name)      # list of emoji strings
    comment = get_comment(name)          # str or None
    mentions = get_mentions(name)        # list of names
    subscribers = get_subscribers(name)  # list of user strings
    endorsements = get_endorsements(name)  # list of endorser strings

    reaction_score = min(len(reactions) * 5, 30)
    comment_score = 10 if comment else 0
    mention_score = min(len(mentions) * 4, 20)
    subscriber_score = min(len(subscribers) * 3, 24)
    endorsement_score = min(len(endorsements) * 8, 40)

    total = reaction_score + comment_score + mention_score + subscriber_score + endorsement_score

    return {
        "reaction_score": reaction_score,
        "comment_score": comment_score,
        "mention_score": mention_score,
        "subscriber_score": subscriber_score,
        "endorsement_score": endorsement_score,
        "total": total,
    }


def engagement_rank() -> list[tuple[str, int]]:
    """Return all snapshots sorted by engagement score descending."""
    results = []
    for name in list_snapshots():
        eng = compute_engagement(name)
        if eng is not None:
            results.append((name, eng["total"]))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def engagement_summary() -> dict:
    """Return aggregate engagement stats across all snapshots."""
    ranked = engagement_rank()
    if not ranked:
        return {"count": 0, "max": 0, "average": 0.0, "top": None}
    scores = [s for _, s in ranked]
    return {
        "count": len(scores),
        "max": max(scores),
        "average": round(sum(scores) / len(scores), 2),
        "top": ranked[0][0],
    }
