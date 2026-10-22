"""Annotated 의존성 별칭을 모아 두는 곳."""

from collections.abc import AsyncIterator, Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.db import AsyncSessionLocal, SessionLocal


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


# 기본: async def 라우트 + AsyncSessionDep
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
# 동기 라이브러리를 같이 쓰는 def 라우트에서만 (FastAPI 가 스레드풀에서 실행)
SessionDep = Annotated[Session, Depends(get_session)]
