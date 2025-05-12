from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import logging

from flask import current_app
from adh6.storage import Base

# # Set up logging
# fileConfig(context.config.config_file_name)
# logger = logging.getLogger('alembic.env')

# Use Flask app's SQLAlchemy config and metadata
config = current_app.config
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config['SQLALCHEMY_ENGINES']['default']
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_server_default=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    def process_revision_directives(context, revision, directives):
        if context.opts.get("autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    engine = engine_from_config(
        {
            "sqlalchemy.url": config['SQLALCHEMY_ENGINES']['default']
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            compare_server_default=True,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
