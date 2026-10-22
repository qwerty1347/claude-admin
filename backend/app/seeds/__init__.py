"""개발·데모용 더미 데이터. 시드 대상 테이블을 비우고 다시 채우므로 운영 DB 에서는 실행하지 않는다.

실행: uv run python -m app.seeds

도메인별 파일(seeds/<도메인>.py)에 seed(session, now) 를 두고, seed_all 에서 차례로 부른다.
운영에도 꼭 필요한 초기 데이터(관리자 계정 등)가 생기면 여기가 아니라 따로 둔다.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.seeds import dashboard


def seed_all(session: Session, now: datetime) -> None:
    """모든 시드를 now 기준으로 넣는다. commit 은 호출하는 쪽이 한다."""
    dashboard.seed(session, now)
