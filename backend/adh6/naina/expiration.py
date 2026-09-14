"""Expiration policy for temporary NainA roles."""

from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

_PARIS = ZoneInfo("Europe/Paris")
_CUTOFF = time(hour=20, minute=30)


def next_naina_expiration(now: datetime) -> datetime:
    """Return the next Paris 20:30 cutoff as a naive UTC datetime."""
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    paris_now = now.astimezone(_PARIS)
    cutoff = datetime.combine(paris_now.date(), _CUTOFF, tzinfo=_PARIS)
    if paris_now >= cutoff:
        cutoff += timedelta(days=1)

    return cutoff.astimezone(UTC).replace(tzinfo=None)
