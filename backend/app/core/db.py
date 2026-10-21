"""DB 기반: 모델의 부모(Base), KST 시각 타입, 엔진·세션.

- 비동기(aiomysql): API 라우트 기본. api/deps.py 의 AsyncSessionDep
- 동기(pymysql): Alembic, 시드, 스크립트, 노트북, 동기 라우트. api/deps.py 의 SessionDep
async def 안에서는 동기 세션을 쓰지 않는다 (이벤트 루프가 막힌다).
"""

from datetime import datetime

from sqlalchemy import DateTime, Dialect, MetaData, create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.types import TypeDecorator

from app.core.config import settings

# 제약 조건 이름 규칙. 이름이 정해져 있어야 Alembic 이 인덱스·FK 를 지우고 바꿀 때 헷갈리지 않는다
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """모든 테이블 모델(app/models/)의 부모"""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class KSTDateTime(TypeDecorator[datetime]):
    """KST DATETIME 컬럼. 파이썬에서는 항상 +09:00 이 붙은 시각으로 다룬다.

    MySQL DATETIME 에는 시간대가 저장되지 않으므로, 저장할 때 KST 로 바꾼 뒤 tzinfo 를 떼고
    읽을 때 settings.tz 를 다시 붙인다.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError(
                "시간대가 없는 datetime 은 저장하지 않는다. clock.now() 를 쓴다"
            )
        return value.astimezone(settings.tz).replace(tzinfo=None)

    def process_result_value(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=settings.tz)


# 끊긴 연결 감지(pre_ping), MySQL wait_timeout 전에 재연결(recycle)
ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 3600}

async_engine = create_async_engine(settings.DATABASE_URL, **ENGINE_OPTIONS)
# expire_on_commit=False: commit 뒤 속성을 읽을 때 다시 조회하지 않는다 (비동기에서는 없으면 에러)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(settings.database_url_sync, **ENGINE_OPTIONS)
SessionLocal = sessionmaker(sync_engine, expire_on_commit=False)
