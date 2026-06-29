"""
비동기 DB 엔진 및 세션 팩토리.

SQLite(개발) -> PostgreSQL(운영) 전환 시:
  1. .env 의 DATABASE_URL만 postgresql+asyncpg://... 로 변경
  2. requirements.txt 의 asyncpg, pgvector 주석 해제 후 재설치
  3. SQLite 전용 connect_args(check_same_thread)는 자동으로 무시되도록
     아래에서 dialect 분기 처리해둠 - 별도 수정 불필요
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

_connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite + aiosqlite 조합에서 멀티스레드 접근 허용
    _connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends용 세션 제너레이터. app/core/deps.py 의 get_db 에서 사용."""
    async with AsyncSessionLocal() as session:
        yield session
