from datetime import UTC, datetime

from adh6.naina.expiration import next_naina_expiration


def test_next_naina_expiration_is_today_at_20_30_in_paris():
    now = datetime(2026, 9, 14, 12, tzinfo=UTC)

    expiration = next_naina_expiration(now)

    assert expiration == datetime(2026, 9, 14, 18, 30, tzinfo=UTC).replace(tzinfo=None)


def test_next_naina_expiration_uses_tomorrows_offset_after_cutoff():
    now = datetime(2026, 10, 24, 19, tzinfo=UTC)

    expiration = next_naina_expiration(now)

    # Daylight saving time ends in Paris on 25 October 2026.
    assert expiration == datetime(2026, 10, 25, 19, 30, tzinfo=UTC).replace(tzinfo=None)
