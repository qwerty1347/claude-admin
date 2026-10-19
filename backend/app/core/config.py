from typing import Literal
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "claude-admin API"
    API_PREFIX: str = "/api"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # 1단계는 Next 서버 컴포넌트가 서버에서 호출하므로 CORS가 필요 없다.
    # 브라우저에서 직접 호출하게 될 때를 대비해 프론트 주소만 허용해 둔다.
    FRONTEND_HOST: str = "http://localhost:3001"

    # 업무 기준 시간대 ('오늘 0시', 화면에 보여줄 시각). 저장·기록은 UTC로 한다. → core/clock.py
    TIMEZONE: str = "Asia/Seoul"

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.TIMEZONE)


settings = Settings()
