# claude-admin

한국어 관리자(Admin) 대시보드예요. 저장소 하나에 프론트와 백엔드가 같이 있어요.

| 폴더 | 내용 |
|---|---|
| `frontend/` | Next.js 16, React 19, TypeScript, Tailwind CSS v4, ECharts 6 |
| `backend/` | FastAPI (Python 3.12, uv), MySQL 9.7 |
| `docs/` | 계획 문서 |

## 실행 (도커)
Docker만 있으면 돼요.

```bash
cp backend/.env.example backend/.env   # 처음 한 번 (개발용 DB 접속 정보가 들어 있어요)
docker compose up -d --build           # 프로젝트 루트에서
```

| 주소 | |
|---|---|
| http://localhost:3001/admin | 관리자 화면 |
| http://localhost:9101/docs | API 문서 |
| `127.0.0.1:3306` | MySQL (`admin` / `admin`, DB `fastapi`) |

- 끄기: `docker compose down` (DB 데이터는 남아요)
- 코드는 저장하면 바로 반영돼요. Dockerfile이나 패키지를 바꿨을 때만 `--build`를 붙여요.
- 한 프로젝트만 띄우려면 그 폴더(`frontend/`, `backend/`)에서 `docker compose up -d`를 실행해요.
- XAMPP MySQL과 포트(3306)가 같아서 동시에 켜지 않아요.

## 실행 (로컬)
Node, uv가 설치돼 있어야 해요.

```bash
cd backend && uv run fastapi dev --port 9101
cd frontend && npm install && npm run dev   # frontend/.env.example 을 .env.local 로 복사
```

## 문서
- `docs/0 DOCKER-PLAN.md`: 도커·모노레포 구성
- `docs/1 PROJECT-PLAN.md`: 초기 설계
- `docs/2 BACKEND-PLAN.md`: 백엔드 계획·규칙
- `docs/3 REALTIME-PLAN.md`: 알림·실시간 기능 검토
