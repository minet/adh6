"""Resync every Kea reservation with ADH6. Meant to run every night, and once after a migration.

    python -m adh6.kea.reconcile [--dry-run] [--kea-url URL ...]

Reads the ADH6 database and the Kea API with the usual settings (DATABASE_*, KEA_API_*).
KEA_ENABLED is not required, so the same image can resync another Kea, for example the
preprod one with --kea-url. Exit code 0 when Kea matches ADH6, 1 when a change failed or ADH6
holds duplicate MACs, 2 when Kea or the configuration is unusable.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from adh6.database import async_session_factory
from adh6.kea.client import KeaClient, KeaError, kea_config_from_settings
from adh6.kea.reservations import reconcile

logger = logging.getLogger("adh6.kea.reconcile")


async def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m adh6.kea.reconcile", description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="log the changes without applying them")
    parser.add_argument("--kea-url", action="append", help="Kea API URL, overrides KEA_API_URLS (repeatable)")
    args = parser.parse_args(argv)

    try:
        config = kea_config_from_settings(args.kea_url)
        async with async_session_factory() as session, KeaClient(config) as client:
            report = await reconcile(client, session, dry_run=args.dry_run)
    except KeaError:
        logger.exception("kea_reconcile_failed")
        return 2

    logger.info(
        "kea_reconcile_done deleted=%s added=%s failed=%s duplicates=%s dry_run=%s",
        report.deleted,
        report.added,
        report.failed,
        len(report.duplicates),
        args.dry_run,
    )
    return 1 if report.failed or report.duplicates else 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    sys.exit(asyncio.run(main(sys.argv[1:])))
