import asyncio
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Import our declarative base and models
from probe.database.base import Base
from probe.database.models import *  # Loads all models
from probe.core.config import get_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    """Retrieve database URL from environment or configuration settings."""
    url = os.getenv("DATABASE_URL")
    if not url:
        settings = get_settings()
        url = getattr(settings, "database_url", None)
    if not url:
        url = config.get_main_option("sqlalchemy.url")
    if url and url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Sync execution runner called within database connection context."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async connection engine."""
    url = get_url()
    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    try:
        # Run async online migrations
        asyncio.run(run_migrations_online())
    except RuntimeError:
        # Loop already running, hook task directly
        loop = asyncio.get_event_loop()
        loop.create_task(run_migrations_online())
