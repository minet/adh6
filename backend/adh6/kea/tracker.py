"""Remember, during a request, which reservations Kea may have to change.

Repositories mark what they touch on the session; adh6.kea.sync reads the marks once the
transaction is committed. A rolled-back transaction discards the session, and its marks with it.

- mark_member: the member's devices may need a new reservation (IP, subnet, room, deletion).
  The devices are looked up after the commit, so a deleted member still works: ADH6 has no
  cascade, its devices stay in the table with their adherent_id.
- mark_mac: a MAC that may no longer exist after the commit (device deleted, MAC changed),
  whose reservations must be checked by MAC.
"""

from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import AsyncSession

_MEMBERS = "kea_member_ids"
_MACS = "kea_macs"
_HEX = re.compile(r"[0-9a-f]{12}")


def normalize_mac(raw: str | None) -> str | None:
    """ADH6 stores MACs as AA-BB-CC-DD-EE-FF; Kea only accepts aa:bb:cc:dd:ee:ff."""
    if not raw:
        return None
    digits = re.sub(r"[-:.\s]", "", raw).lower()
    if not _HEX.fullmatch(digits):
        return None
    return ":".join(digits[i : i + 2] for i in range(0, 12, 2))


def mark_member(session: AsyncSession, member_id: int | None) -> None:
    if member_id is not None:
        session.info.setdefault(_MEMBERS, set()).add(member_id)


def mark_mac(session: AsyncSession, mac: str | None) -> None:
    normalized = normalize_mac(mac)
    if normalized is not None:
        session.info.setdefault(_MACS, set()).add(normalized)


def pop_marks(session: AsyncSession) -> tuple[set[int], set[str]]:
    members: set[int] = session.info.pop(_MEMBERS, set())
    macs: set[str] = session.info.pop(_MACS, set())
    return members, macs
