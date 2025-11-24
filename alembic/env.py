import asyncio
from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool, Connection
from sqlalchemy.ext.asyncio import create_async_engine

from sqlmodel import SQLModel
from models import *

from environs import Env

env = Env()

env.read_env()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

DATABASE_URL = env.str("DATABASE_URL")

if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

EXCLUDED_TABLES = {
    "account_emailaddress", "django_migrations", "account_emailconfirmation", 
    "spatial_ref_sys", "auth_permission", "auth_user", "auth_user_groups",
    "auth_user_user_permissions", "authtoken_token", "auth_group", 
    "django_content_type", "django_admin_log", "django_session", 
    "socialaccount_socialaccount", "socialaccount_socialapp", 
    "socialaccount_socialtoken"
}

def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in EXCLUDED_TABLES:
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations synchronously using the connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async."""
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
