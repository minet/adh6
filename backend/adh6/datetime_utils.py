"""Datetime helpers for the application's timezone conventions."""

from datetime import UTC, date, datetime


def utc_now_naive() -> datetime:
    """Return the current UTC time in the naive format used by SQL columns."""
    return datetime.now(UTC).replace(tzinfo=None)


def utc_today() -> date:
    """Return the current calendar date according to the container's UTC clock."""
    return datetime.now(UTC).date()


MIN_UTC_NAIVE = datetime(1, 1, 1, tzinfo=UTC).replace(tzinfo=None)
