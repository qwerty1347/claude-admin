from fastapi.testclient import TestClient

from app.core.config import settings


def test_health_check(client: TestClient) -> None:
    r = client.get(f"{settings.API_PREFIX}/v1/utils/health-check/")
    assert r.status_code == 200
    assert r.json() == {"statusCode": 200, "code": "OK", "data": True}
