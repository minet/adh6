from alembic import context
from sqlalchemy import create_engine

from adh6.config.configuration import settings
from adh6.storage import Base

target_metadata = Base.metadata


def _sync_url() -> str:
    return (
        settings.database_url
        .replace("+aiosqlite", "")
        .replace("+aiomysql", "+pymysql")
    )


def run_migrations_offline() -> None:
    context.configure(url=_sync_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(_sync_url())
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
