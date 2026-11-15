"""Push the reservations touched by a request to Kea, once its transaction is committed.

Never raises: if Kea is down or refuses a command, the change stays saved in ADH6, a warning is
logged, and the periodic `python -m adh6.kea.reconcile` fixes Kea. The whole sync is bounded by
KEA_SYNC_BUDGET_SECONDS, since it runs before the response is sent.
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from adh6.config.configuration import settings
from adh6.kea.client import KeaClient, kea_config_from_settings
from adh6.kea.reservations import macs_of_members, sync_macs
from adh6.kea.tracker import pop_marks

logger = logging.getLogger(__name__)


async def sync_after_commit(session: AsyncSession) -> None:
    member_ids, macs = pop_marks(session)
    if not settings.kea_enabled or not (member_ids or macs):
        return
    try:
        async with asyncio.timeout(settings.kea_sync_budget_seconds):
            macs |= await macs_of_members(session, member_ids)
            async with KeaClient(kea_config_from_settings()) as client:
                report = await sync_macs(client, session, macs)
    except Exception:
        logger.warning("kea_sync_failed members=%s macs=%s", sorted(member_ids), sorted(macs), exc_info=True)
        return
    if report.failed or report.duplicates:
        logger.warning(
            "kea_sync_incomplete failed=%s duplicates=%s members=%s",
            report.failed,
            len(report.duplicates),
            sorted(member_ids),
        )
