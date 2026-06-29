"""
Alembic 환경 설정.
비동기 엔진(SQLAlchemy 2.0 async)에 맞춰 run_migrations_online을 구성했다.

사용법:
  alembic revision --autogenerate -m "init"
  alembic upgrade head
"""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.base import Base

# app/models/__init__.py 에서 모든 모델을 import해두었으므로,
# 아래 한 줄로 Base.metadata가 전체 테이블 정의를 인식한다.
import app.models  # noqa: F401

config = context.config

# .env의 DATABASE_URL을 alembic.ini 설정보다 우선 적용
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """`alembic upgrade head --sql` 같은 오프라인 모드용."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
