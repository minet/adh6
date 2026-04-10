"""Legacy synchronous DB facade used by historical tests.

The application itself uses async sessions from ``adh6.database``. This module
only keeps compatibility for tests that still call ``db.session`` directly.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from adh6.config.configuration import settings


def _to_sync_url(url: str) -> str:
    if url.startswith("mysql+aiomysql://"):
        return url.replace("mysql+aiomysql://", "mysql+mysqldb://", 1)
    if url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return url


class _LegacyDb:
    def __init__(self):
        self.engine = create_engine(_to_sync_url(settings.database_url), future=True)
        self._session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = self._session_factory()
        return self._session

    @property
    def sessionmaker(self):
        """Expose session factory for tests."""
        return self._session_factory


db = _LegacyDb()
