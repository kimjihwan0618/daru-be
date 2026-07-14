# gwiteem Backend

출퇴근 맞춤 브리핑 서비스 백엔드 (FastAPI + SQLite → PostgreSQL/pgvector 전환 예정)

> 이 저장소는 **전체 엔드포인트 + DB 모델 뼈대**까지 생성된 상태입니다.
> 비즈니스 로직(서비스/외부 API 연동/RAG)은 각 파일의 `TODO(구현 필요)` 주석을 따라 직접 구현하시면 됩니다.
> 전체 설계 의도는 `docs/gwiteem_API_설계서.md` (별도 전달됨)를 참고하세요.

---

## 1. 빠른 시작

```bash
# 1. 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 파일 생성
copy .env.example .env         # Windows
# cp .env.example .env         # macOS/Linux
# .env 파일을 열어 최소한 JWT_SECRET_KEY는 임의의 랜덤 문자열로 변경하세요.

# 4. DB 마이그레이션 (최초 1회 모델 생성 후 실행)
alembic revision --autogenerate -m "init"
alembic upgrade head

# 5. 서버 실행
uvicorn app.main:app --reload
```

서버가 뜨면:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

> **현재 모든 엔드포인트는 `raise NotImplementedError`로 응답합니다.**
> 라우터 자체는 호출되고 422(요청 형식 오류)는 정상적으로 검증되지만,
> 실제 데이터 응답은 서비스 로직을 구현해야 동작합니다.

---

## 2. 프로젝트 구조

```
app/
├── main.py            # FastAPI 앱 진입점, 라우터 등록, 예외 핸들러
├── core/              # 설정, JWT, 공용 Dependency(인증), 커스텀 예외
├── db/                # DB 엔진/세션, Alembic 마이그레이션
├── models/            # SQLAlchemy ORM 모델 (테이블 정의 완료)
├── schemas/           # Pydantic 요청/응답 스키마 (정의 완료)
├── routers/           # API 엔드포인트 (경로/시그니처 완료, 로직은 TODO)
├── services/          # 비즈니스 로직 뼈대 (구현 필요)
├── repositories/       # DB 쿼리 캡슐화 (일부 기본 조회만 구현됨)
├── external/          # 외부 API 클라이언트 뼈대 (구현 필요)
└── workers/           # Celery 비동기 작업 뼈대 (구현 필요)
```

**계층 의존 규칙**: `routers → services → repositories → models`
라우터에서 직접 DB 쿼리를 작성하지 말고, services를 거쳐 repositories를 호출하세요.

---

## 3. 구현 우선순위 가이드

설계서 9장 "개발 착수 순서"를 따르는 것을 권장합니다.

1. **인증** (`app/services/auth_service.py`, `app/external/oauth_client.py`)
   - 소셜 로그인 1개(카카오 추천 - 한국 사용자 기준 진입장벽 낮음)부터 끝까지 구현
   - JWT 발급/검증은 `app/core/security.py`에 이미 구현되어 있음 (바로 사용 가능)

2. **읽기 전용 기능** (종목/교통/날씨) - RAG 없이 동작, 외부 API 연동 패턴 학습에 좋음
   - `app/external/stock_price_client.py`, `map_directions_client.py`, `weather_client.py`

3. **뉴스 수집 파이프라인**
   - `app/external/naver_news_client.py` → `app/workers/tasks_news_collect.py`

4. **임베딩 + 중복제거 (RAG 1단계)**
   - `app/external/openai_client.py`의 `create_embedding` 먼저 구현
   - `app/services/rag_service.py`의 `cosine_similarity`, `find_similar_issue_clusters`
   - `app/services/news_dedup_service.py`

5. **이슈 요약 + 공통 브리핑 생성**
   - `app/services/rag_service.py`의 `summarize_issue_cluster`
   - `app/workers/tasks_briefing_generate.py`

6. **관심 키워드/종목 + 게스트→로그인 마이그레이션**
   - `app/routers/interest.py`의 TODO들

7. **개인화 브리핑 (RAG 2단계: 전체 RAG 파이프라인 완성)**
   - `app/services/rag_service.py`의 `generate_personalized_briefing`
   - `app/services/briefing_service.py`

---

## 4. SQLite → PostgreSQL(pgvector) 전환 시 체크리스트

1. `.env`의 `DATABASE_URL`을 PostgreSQL DSN으로 변경
2. `requirements.txt`의 `asyncpg`, `pgvector` 주석 해제 후 `pip install -r requirements.txt` 재실행
3. `app/models/news.py` 상단 docstring의 가이드대로 `NewsEmbedding.embedding`,
   `InterestEmbedding.embedding` 컬럼을 `Vector(1536)` 타입으로 교체
4. Alembic migration에서 `CREATE EXTENSION IF NOT EXISTS vector;` 추가
5. HNSW 인덱스 추가: `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)`
6. `app/services/rag_service.py`의 `cosine_similarity`(애플리케이션 레벨 계산)를
   SQL `<=>` 연산자 기반 쿼리로 교체
7. `docker-compose.yml`로 로컬 PostgreSQL+pgvector, Redis 기동

---

## 5. 미해결 설계 메모 (구현 중 결정 필요)

코드 내 TODO 외에, 모델/엔드포인트 설계 시 의도적으로 보류한 항목들입니다:

- **users.preferences**: 브리핑 알림 시간/푸시 설정을 저장할 테이블이 ERD에 없습니다.
  `app/routers/user.py`의 `/users/me/preferences` 구현 전, `users` 테이블에 컬럼을 추가하거나
  별도 `user_preferences` 테이블을 만들지 결정 필요.
- **브리핑 피드백(👍👎) 저장 테이블**: 마찬가지로 ERD에 없어 추가 설계 필요.
- **공유 링크 만료 정책**: `SharedBriefing` 모델에 `expires_at` 컬럼이 없습니다. 필요 시 추가.
- **(user_id, type, value) 등 unique 제약**: 각 모델 파일에 TODO로 표시해두었으니
  Alembic migration 작성 시 함께 추가하는 것을 권장합니다.

---

## 6. 테스트

```bash
pytest app/tests/
```
현재 `app/tests/`는 비어 있습니다. 서비스 로직 구현과 함께 테스트를 추가하세요.
