"""Alembic 실행 환경. 마이그레이션은 동기 드라이버(pymysql)로 실행한다.

접속 주소는 app 설정(settings.database_url_sync)을 쓰고, 테이블 정의는 app.models 에서 가져온다.
"""

from logging.config import fileConfig
from typing import Any, Literal

from alembic import context
from alembic.autogenerate.api import AutogenContext
from sqlalchemy import engine_from_config, pool

from app import models  # noqa: F401  모든 모델을 import 해야 autogenerate 가 테이블을 찾는다
from app.core.config import settings
from app.core.db import Base, KSTDateTime

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# configparser 는 % 를 특수 문자로 보므로 비밀번호 등에 % 가 있으면 %% 로 바꿔 넣는다
config.set_main_option("sqlalchemy.url", settings.database_url_sync.replace("%", "%%"))

target_metadata = Base.metadata


def render_item(
    type_: str, obj: Any, _autogen_context: AutogenContext
) -> str | Literal[False]:
    """KSTDateTime 컬럼은 마이그레이션 파일에 sa.DateTime() 으로 쓴다.

    DB 에는 그냥 DATETIME 이고, 시간대 변환은 앱 코드의 일이다.
    마이그레이션 파일이 app 코드를 import 하지 않아야 나중에 코드가 바뀌어도 옛 마이그레이션이 깨지지 않는다.
    """
    if type_ == "type" and isinstance(obj, KSTDateTime):
        return "sa.DateTime()"
    return False


def run_migrations_offline() -> None:
    """DB 에 접속하지 않고 SQL 만 출력한다 (alembic upgrade head --sql)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
