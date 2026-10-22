"""uv run python -m app.seeds"""

import logging

from app.core import clock
from app.core.db import SessionLocal
from app.seeds import seed_all

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    now = clock.now()
    logger.info("시드 시작 (기준 시각 %s)", now.isoformat(timespec="minutes"))
    with SessionLocal() as session:
        seed_all(session, now)
        session.commit()
    logger.info("시드 완료")


if __name__ == "__main__":
    main()
