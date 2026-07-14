# gwiteem 백엔드 API 설계서

> 출퇴근 맞춤 브리핑 서비스 — FastAPI + PostgreSQL(pgvector) + RAG

---

## 1. 프로젝트 개요

### 1.1 서비스 정의
gwiteem은 사용자의 출퇴근 시간에 맞춰 **뉴스, 금융, 교통, 날씨**를 하나의 짧은 브리핑으로 압축해주는 서비스다.
비로그인 사용자에게는 "오늘의 공통 브리핑"을, 로그인 사용자에게는 **관심 종목·키워드 기반 RAG 개인화 브리핑**을 제공한다.

### 1.2 기술 스택

| 영역 | 기술 | 선정 이유 |
|---|---|---|
| API 서버 | FastAPI (Python 3.12) | 비동기 I/O, 자동 OpenAPI 문서화, RAG 파이프라인과의 Python 생태계 호환성 |
| RDBMS | PostgreSQL 16 | 정형 데이터(사용자/종목/일정) 관리 |
| Vector DB | **pgvector** (PostgreSQL extension) | 별도 인프라 없이 RDBMS와 벡터 검색을 한 트랜잭션에서 처리. 초기~중기 트래픽에 적합, 추후 Qdrant 등으로 마이그레이션 경로 명확 |
| ORM | SQLAlchemy 2.0 (async) + Alembic | 비동기 쿼리, 마이그레이션 관리 |
| LLM / Embedding | OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`) | 한국어 품질·비용·생태계 균형, RAG 레퍼런스 풍부 |
| 인증 | OAuth2 소셜 로그인(카카오/네이버/구글) + 자체 JWT(access/refresh) 발급 | 가입 마찰 최소화 + 서버 자체 세션 제어 |
| 비동기 작업 | Celery + Redis (또는 APScheduler로 단순화 가능) | 뉴스 수집·임베딩·브리핑 생성의 주기적 배치 처리 |
| 캐시 | Redis | 공통 브리핑, 종목 시세 등 TTL 캐싱 |
| 외부 연동 | 네이버 뉴스 검색 API, 언론사 RSS, 증권 시세 API(예: 한국투자증권 OpenAPI), 카카오맵/네이버맵 길찾기 API, 기상청 API | 데이터 소스 |

### 1.3 핵심 설계 철학
1. **비로그인/로그인 기능 분리**: 동일 엔드포인트라도 인증 토큰 유무에 따라 응답이 달라지는 구조(Optional Auth)와, 로그인 전용 엔드포인트(시작에 `/me/`)를 명확히 구분한다.
2. **뉴스 파이프라인은 배치(오프라인)와 서빙(온라인)을 분리**한다. 수집·중복제거·임베딩·요약은 스케줄러가 미리 처리해두고, API는 이미 가공된 결과를 빠르게 읽기만 한다.
3. **RAG는 "개인화 브리핑 생성"에 집약**한다. 사용자의 관심 키워드/종목 임베딩 → 유사 뉴스 클러스터 retrieval → LLM 요약 생성이 이 프로젝트의 핵심 학습 포인트다.

---

## 2. 시스템 아키텍처

```
┌─────────────┐        ┌──────────────────────────────────────────────┐
│   Client    │  HTTPS │                FastAPI App                    │
│ (Web/App)   ├───────►│  routers/ → services/ → repositories/ → models │
└─────────────┘        └───────────────┬────────────────────────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              ▼                         ▼                         ▼
      ┌───────────────┐        ┌────────────────┐        ┌────────────────┐
      │  PostgreSQL    │        │     Redis       │        │  외부 API       │
      │  + pgvector    │        │ (캐시/세션/큐)  │        │ 뉴스/시세/교통/날씨│
      └───────┬───────┘        └────────────────┘        └───────┬────────┘
              ▲                                                    │
              │              ┌─────────────────────┐               │
              └──────────────┤  Celery Worker/Beat  ├───────────────┘
                              │ (뉴스수집→중복제거    │
                              │  →임베딩→이슈요약     │
                              │  →개인화 브리핑 생성)  │
                              └──────────┬───────────┘
                                         ▼
                                ┌─────────────────┐
                                │  OpenAI API      │
                                │ Embedding / LLM  │
                                └─────────────────┘
```

### 2.1 데이터 흐름 (뉴스 파이프라인, 배치)
1. **수집**: Celery Beat가 5~10분 주기로 네이버뉴스 API/언론사 RSS에서 기사 수집 → `raw_articles` 저장
2. **중복 제거 + 클러스터링**: 신규 기사 본문을 임베딩(`text-embedding-3-small`) → pgvector의 코사인 유사도로 기존 클러스터와 비교 → 유사도 threshold 이상이면 기존 `issue_cluster`에 합류, 아니면 신규 클러스터 생성
3. **이슈 요약**: 클러스터 내 기사가 일정 개수 이상 모이면 LLM으로 핵심 이슈 1줄 요약 + 카테고리 태깅 → `issue_clusters.summary` 갱신
4. **공통 브리핑 생성**: 하루 1~2회(예: 06:00, 17:00), 상위 이슈들을 모아 "3분 브리핑" 텍스트를 LLM으로 생성 → `daily_briefings`에 저장 (모든 비로그인 사용자가 공유)
5. **개인화 브리핑 생성(로그인 사용자)**: 사용자의 관심 키워드/종목 임베딩과 가장 유사한 이슈 클러스터를 retrieval → 공통 브리핑 베이스 + 개인 관심사 하이라이트를 LLM으로 재구성 → `user_briefings`에 캐싱

### 2.2 데이터 흐름 (API 서빙, 온라인)
- 클라이언트는 항상 **이미 생성되어 캐싱된 브리핑/이슈**를 조회한다 (API 응답 시간 내 LLM 호출 최소화 원칙).
- 예외: "종목 검색 → 관련 뉴스", "출발지·도착지 일회성 교통조회"는 사용자 요청 시점에 실시간으로 외부 API를 호출하는 게 자연스러워 온디맨드로 처리한다.

---

## 3. 프로젝트 폴더 구조

```
gwiteem/BE/
├── app/
│   ├── main.py                      # FastAPI 앱 진입점
│   ├── core/
│   │   ├── config.py                 # 환경설정 (Pydantic Settings)
│   │   ├── security.py               # JWT 발급/검증, 비밀번호 해시
│   │   ├── deps.py                   # 공용 Dependency (get_db, get_current_user, get_optional_user)
│   │   └── exceptions.py             # 커스텀 예외 + 핸들러
│   │
│   ├── db/
│   │   ├── base.py                   # Declarative Base
│   │   ├── session.py                # 비동기 엔진/세션
│   │   └── migrations/               # Alembic
│   │
│   ├── models/                       # SQLAlchemy ORM 모델
│   │   ├── user.py
│   │   ├── stock.py
│   │   ├── news.py                   # RawArticle, IssueCluster, NewsEmbedding(pgvector)
│   │   ├── briefing.py
│   │   ├── schedule.py
│   │   └── commute.py
│   │
│   ├── schemas/                      # Pydantic 요청/응답 스키마
│   │   ├── auth.py
│   │   ├── briefing.py
│   │   ├── news.py
│   │   ├── stock.py
│   │   ├── commute.py
│   │   └── user.py
│   │
│   ├── routers/                      # API 엔드포인트 (얇게, 서비스 호출만)
│   │   ├── auth.py
│   │   ├── briefing.py
│   │   ├── news.py
│   │   ├── stock.py
│   │   ├── commute.py
│   │   ├── interest.py               # 관심 키워드/종목, 비로그인 임시선택 포함
│   │   ├── schedule.py
│   │   └── user.py
│   │
│   ├── services/                     # 비즈니스 로직
│   │   ├── auth_service.py
│   │   ├── briefing_service.py       # 브리핑 조합/캐싱 조회 로직
│   │   ├── rag_service.py            # retrieval + LLM 프롬프트 조립 (핵심)
│   │   ├── news_dedup_service.py     # 임베딩 유사도 기반 중복제거/클러스터링
│   │   ├── stock_service.py
│   │   ├── commute_service.py
│   │   └── share_service.py
│   │
│   ├── repositories/                 # DB 접근 계층 (쿼리 캡슐화)
│   │   ├── user_repo.py
│   │   ├── news_repo.py
│   │   ├── briefing_repo.py
│   │   └── stock_repo.py
│   │
│   ├── external/                     # 외부 API 클라이언트
│   │   ├── naver_news_client.py
│   │   ├── stock_price_client.py
│   │   ├── map_directions_client.py
│   │   ├── weather_client.py
│   │   └── openai_client.py
│   │
│   ├── workers/                      # Celery 작업
│   │   ├── celery_app.py
│   │   ├── tasks_news_collect.py
│   │   ├── tasks_news_dedup.py
│   │   ├── tasks_briefing_generate.py
│   │   └── beat_schedule.py
│   │
│   └── tests/
│       ├── test_auth.py
│       ├── test_briefing.py
│       └── test_news.py
│
├── alembic.ini
├── requirements.txt
├── docker-compose.yml                # postgres(pgvector), redis, app, worker
├── Dockerfile
└── .env.example
```

**계층 의존 규칙**: `routers → services → repositories → models`. routers는 DB 세션/쿼리를 직접 다루지 않고 services만 호출한다. 이렇게 분리해두면 추후 RAG 로직(`rag_service`)만 따로 떼어 테스트/교체하기 쉽다.

---

## 4. 데이터베이스 설계 (ERD 개요)

### 4.1 RDBMS 테이블

```
users
├─ id (PK)
├─ email
├─ nickname
├─ provider (kakao/naver/google)
├─ provider_id
├─ profile_image_url
├─ created_at / updated_at
└─ last_login_at

user_interests                     # 로그인 사용자의 영구 관심 키워드/종목
├─ id (PK)
├─ user_id (FK → users)
├─ type (KEYWORD / STOCK)
├─ value (예: "HBM", "삼성전자")
└─ created_at

guest_interests                     # 비로그인 임시 선택 (세션/디바이스 토큰 기반)
├─ id (PK)
├─ session_token                    # 쿠키 또는 클라이언트 생성 UUID
├─ type (KEYWORD / STOCK)
├─ value
└─ expires_at                       # TTL (예: 24시간)

stocks                              # 종목 마스터
├─ id (PK)
├─ code (종목코드, 예: 005930)
├─ name (예: 삼성전자)
├─ market (KOSPI/KOSDAQ)
└─ updated_at

raw_articles                        # 수집된 원본 기사
├─ id (PK)
├─ source (언론사명)
├─ title
├─ url
├─ published_at
├─ content_snippet
├─ category (반도체/금리/AI 등 1차 분류)
├─ cluster_id (FK → issue_clusters, nullable)
└─ created_at

issue_clusters                      # 중복 제거된 핵심 이슈
├─ id (PK)
├─ title (예: "HBM 공급계약 확대 기대감에 반도체 업종 강세")
├─ summary (LLM 생성 요약)
├─ category
├─ article_count
├─ centroid_embedding_id (FK → news_embeddings)   # 클러스터 대표 벡터 참조
├─ related_stock_codes (array 또는 별도 매핑 테이블)
├─ created_at / updated_at
└─ is_active (당일 브리핑 노출 여부)

daily_briefings                     # 공통 브리핑 (비로그인 포함 전체 공유)
├─ id (PK)
├─ briefing_date
├─ time_slot (MORNING/EVENING)
├─ summary_text (3분 브리핑 본문)
├─ top_issue_ids (array, issue_clusters 참조)
└─ generated_at

user_briefings                      # 로그인 사용자 개인화 브리핑 캐시
├─ id (PK)
├─ user_id (FK → users)
├─ briefing_date
├─ time_slot
├─ personalized_text
├─ matched_issue_ids (array)
└─ generated_at

commute_routes                      # 사용자가 등록한 집/회사 (로그인 시 고정)
├─ id (PK)
├─ user_id (FK → users)
├─ label (집/회사)
├─ address
├─ latitude / longitude
└─ is_default

commute_queries                     # 비로그인 포함 모든 일회성 교통조회 로그
├─ id (PK)
├─ user_id (FK, nullable)            # 비로그인이면 null
├─ origin_address / dest_address
├─ origin_lat / origin_lng
├─ dest_lat / dest_lng
├─ estimated_minutes
├─ delay_minutes
└─ queried_at

schedules                           # 오늘의 일정 (증시개장, 경제지표 발표 등 시스템 일정 + 사용자 일정)
├─ id (PK)
├─ user_id (FK, nullable)            # null이면 전체 공통 일정(증시개장 등)
├─ title
├─ scheduled_time
├─ category (MARKET/ECONOMIC/COMMUTE/CUSTOM)
└─ schedule_date

shared_briefings                    # 브리핑 공유 (공유 링크)
├─ id (PK)
├─ briefing_type (DAILY/USER)
├─ briefing_ref_id
├─ share_token (UUID)
├─ created_by_user_id (nullable)
└─ created_at
```

### 4.2 Vector DB 테이블 (pgvector)

```
news_embeddings
├─ id (PK)
├─ article_id (FK → raw_articles)
├─ embedding (vector(1536))          -- text-embedding-3-small 차원
└─ created_at

interest_embeddings                  # 사용자/게스트 관심 키워드의 임베딩 (RAG retrieval용)
├─ id (PK)
├─ owner_type (USER/GUEST)
├─ owner_ref_id (user_id 또는 guest session_token)
├─ keyword
├─ embedding (vector(1536))
└─ updated_at
```

> **인덱스**: `news_embeddings.embedding`, `interest_embeddings.embedding`에 `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)` 적용 (pgvector 0.5+ HNSW 권장).

---
## 5. 인증 및 공통 규칙

### 5.1 인증 흐름
```
1. 클라이언트가 소셜 로그인(카카오/네이버/구글) 진행 → provider의 authorization code 획득
2. POST /api/v1/auth/{provider}/callback 에 code 전달
3. 서버가 provider에 code로 토큰 교환 → 사용자 식별 정보(email, nickname 등) 획득
4. 최초 로그인이면 users 테이블에 신규 생성, 기존 유저면 last_login_at 갱신
5. 서버 자체 JWT access_token(단기, 30분) + refresh_token(장기, 14일) 발급
6. 이후 요청은 Authorization: Bearer {access_token} 헤더로 인증
7. access_token 만료 시 POST /api/v1/auth/refresh 로 재발급
```

### 5.2 인증 구분 3가지 패턴
- **`Public`**: 인증 불필요. 누구나 호출 가능 (예: 공통 브리핑 조회)
- **`Optional Auth`**: 토큰이 있으면 개인화 응답, 없으면 게스트(공통) 응답. (예: 오늘의 브리핑, 관심 키워드)
- **`Required Auth`**: 토큰 필수. 없으면 401. (경로 prefix에 `/me` 사용 — 예: `/users/me/interests`)

### 5.3 게스트 식별
- 비로그인 사용자의 "관심 키워드 임시 선택"은 서버가 발급하는 `X-Guest-Session-Id` (UUID, 쿠키 또는 헤더)로 식별한다.
- 클라이언트가 헤더 없이 첫 요청을 보내면 서버가 신규 UUID를 생성해 응답 헤더로 내려준다.
- `guest_interests`, `commute_queries`는 이 UUID로 매칭하며 TTL 24시간 후 만료.

### 5.4 공통 응답 포맷
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```
에러 시:
```json
{
  "success": false,
  "data": null,
  "error": { "code": "STOCK_NOT_FOUND", "message": "해당 종목을 찾을 수 없습니다." }
}
```

### 5.5 공통 에러 코드
| HTTP Status | code | 설명 |
|---|---|---|
| 400 | `INVALID_REQUEST` | 요청 파라미터 오류 |
| 401 | `UNAUTHORIZED` | 토큰 없음/만료 |
| 403 | `FORBIDDEN` | 권한 없음(타인 리소스 접근 등) |
| 404 | `NOT_FOUND` | 리소스 없음 |
| 409 | `CONFLICT` | 중복 데이터 (예: 이미 등록된 관심 종목) |
| 429 | `TOO_MANY_REQUESTS` | Rate limit 초과 |
| 500 | `INTERNAL_ERROR` | 서버 오류 |

### 5.6 페이지네이션 규칙
리스트 응답은 cursor 기반을 기본으로 한다 (뉴스 피드처럼 계속 추가되는 데이터에 적합).
```
GET /api/v1/news/issues?cursor=eyJpZCI6MTIzfQ&limit=20
```
응답에 `next_cursor` 포함, 없으면 `null`.

---
## 6. 엔드포인트 명세

> 모든 경로는 `/api/v1` prefix 기준. 인증 구분: `Public` / `Optional` / `Required`

### 6.1 인증 (Auth)

#### `GET /auth/{provider}/login-url`
- **인증**: Public
- **설명**: 소셜 로그인 진입 URL 발급 (provider: kakao/naver/google)
- **Query**: 없음
- **Response 200**
```json
{ "success": true, "data": { "login_url": "https://kauth.kakao.com/oauth/authorize?..." } }
```

#### `POST /auth/{provider}/callback`
- **인증**: Public
- **설명**: 소셜 로그인 콜백 처리 → 회원가입/로그인 + JWT 발급
- **Request Body**
```json
{ "code": "authorization_code_from_provider" }
```
- **Response 200**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 1800,
    "is_new_user": true,
    "user": { "id": 1, "nickname": "지환", "profile_image_url": "..." }
  }
}
```

#### `POST /auth/refresh`
- **인증**: Public (refresh_token 자체가 인증 수단)
- **Request Body**: `{ "refresh_token": "eyJ..." }`
- **Response 200**: 새 `access_token` 발급
- **Error**: refresh_token 만료/위조 시 401 `INVALID_REFRESH_TOKEN`

#### `POST /auth/logout`
- **인증**: Required
- **설명**: refresh_token 무효화 (서버 측 블랙리스트 또는 DB 삭제)
- **Response 200**: `{ "success": true, "data": null }`

#### `DELETE /auth/withdraw`
- **인증**: Required
- **설명**: 회원 탈퇴 (관련 interests, briefings 등 cascade 삭제)

---

### 6.2 오늘의 브리핑 (Briefing)

#### `GET /briefings/today`
- **인증**: Optional
- **설명**: 메인 화면의 "오늘의 브리핑" 카드. 비로그인이면 공통 브리핑(`daily_briefings`), 로그인이면 개인화 브리핑(`user_briefings`)을 반환. 개인화 브리핑이 아직 생성 전이면 공통 브리핑 + `is_personalized: false`로 즉시 응답(생성은 비동기로 트리거).
- **Query**: `time_slot` (옵션, MORNING/EVENING, 미지정시 현재 시각 기준 자동 판단)
- **Response 200**
```json
{
  "success": true,
  "data": {
    "briefing_date": "2026-06-29",
    "time_slot": "MORNING",
    "greeting": "좋은 아침, 지환님",
    "headline": "오늘은 8:10까지 출발하세요",
    "subtext": "분당수서로 사고로 평소보다 12분 더 걸려요",
    "weather": { "temp_c": 21, "condition": "맑음" },
    "summary_text": "...3분 브리핑 전문...",
    "is_personalized": true,
    "key_changes": [
      {
        "id": 1,
        "icon": "CHIP",
        "text": "HBM 공급계약 이슈가 관심 종목에 영향을 줄 수 있어요",
        "issue_id": 501
      },
      { "id": 2, "icon": "BANK", "text": "미국 금리 발언이 오늘 국내 증시의 핵심 변수예요", "issue_id": 502 },
      { "id": 3, "icon": "TEMP", "text": "퇴근 시간 기온이 아침보다 9°C 낮아요", "issue_id": null }
    ],
    "updated_at": "2026-06-29T07:28:00+09:00"
  }
}
```

#### `GET /briefings/today/changes/{change_id}/evidence`
- **인증**: Optional
- **설명**: "근거 보기" — 중요 변화 항목의 출처 근거(원본 기사/데이터) 상세
- **Response 200**
```json
{
  "success": true,
  "data": {
    "change_id": 1,
    "explanation": "최근 18건의 반도체 관련 기사가 HBM 공급계약 확대를 다루고 있으며, 삼성전자·SK하이닉스 주가에 직접 영향을 주고 있습니다.",
    "source_articles": [
      { "title": "삼성전자, HBM4 공급계약 확대 논의", "source": "한국경제", "url": "...", "published_at": "2026-06-29T06:10:00+09:00" }
    ]
  }
}
```

#### `POST /briefings/today/share`
- **인증**: Optional
- **설명**: 브리핑 공유 링크 생성
- **Response 200**
```json
{ "success": true, "data": { "share_url": "https://gwiteem.com/s/4f9a2b", "expires_at": "2026-07-06T00:00:00+09:00" } }
```

#### `GET /briefings/shared/{share_token}`
- **인증**: Public
- **설명**: 공유받은 브리핑 조회 (공유 당시 시점의 스냅샷 반환)

#### `POST /briefings/today/feedback`
- **인증**: Optional
- **설명**: "오늘 브리핑이 유용했나요?" 👍👎 피드백 수집
- **Request Body**: `{ "is_helpful": true }`

---

### 6.3 주제별 브리핑 (Topic Briefing)

#### `GET /briefings/topics`
- **인증**: Public
- **설명**: 이용 가능한 주제 목록 (AI/반도체/경제 등)
- **Response 200**
```json
{ "success": true, "data": [
  { "code": "SEMICONDUCTOR", "label": "반도체", "article_count_today": 18 },
  { "code": "RATE", "label": "금리", "article_count_today": 4 },
  { "code": "AI", "label": "AI", "article_count_today": 2 }
] }
```

#### `GET /briefings/topics/{topic_code}`
- **인증**: Public
- **설명**: 특정 주제의 브리핑 본문 + 관련 이슈 클러스터 리스트
- **Response 200**
```json
{
  "success": true,
  "data": {
    "topic_code": "SEMICONDUCTOR",
    "label": "반도체",
    "summary_text": "HBM 공급계약 확대 기대감에 반도체 업종 전반이 강세를 보이고 있습니다...",
    "issues": [
      {
        "id": 501,
        "title": "HBM 공급계약 확대 기대감에 반도체 업종 강세",
        "article_count": 18,
        "thumbnail_url": "...",
        "source_logos": ["연합뉴스", "한경", "매경"],
        "updated_at": "2026-06-29T07:00:00+09:00"
      }
    ]
  }
}
```

---
### 6.4 뉴스/이슈 (News)

#### `GET /news/issues`
- **인증**: Public
- **설명**: "중복 뉴스 N건을 M개 이슈로 정리" 리스트. 메인 하단 카드 영역.
- **Query**: `category` (옵션), `cursor`, `limit` (default 10)
- **Response 200**
```json
{
  "success": true,
  "data": {
    "total_raw_articles": 24,
    "total_issues": 3,
    "issues": [
      {
        "id": 501,
        "category": "반도체",
        "article_count": 18,
        "title": "HBM 공급계약 확대 기대감에 반도체 업종 강세",
        "thumbnail_url": "https://...",
        "source_logos": ["인포스탁", "한경", "매경"],
        "extra_source_count": 15
      }
    ],
    "next_cursor": null
  }
}
```

#### `GET /news/issues/{issue_id}`
- **인증**: Public
- **설명**: 이슈 상세 — 요약 + 원문 기사 목록
- **Response 200**
```json
{
  "success": true,
  "data": {
    "id": 501,
    "title": "HBM 공급계약 확대 기대감에 반도체 업종 강세",
    "summary": "...",
    "category": "반도체",
    "related_stocks": [{ "code": "005930", "name": "삼성전자" }, { "code": "000660", "name": "SK하이닉스" }],
    "articles": [
      { "title": "...", "source": "한국경제", "url": "...", "published_at": "..." }
    ]
  }
}
```

#### `GET /news/search`
- **인증**: Public
- **설명**: 키워드로 뉴스/이슈 검색 (간단 텍스트 검색, RAG retrieval과 별개)
- **Query**: `q` (필수), `cursor`, `limit`

---

### 6.5 종목 (Stock)

#### `GET /stocks/search`
- **인증**: Public
- **설명**: 종목명/코드로 검색 (자동완성)
- **Query**: `q` (필수, 예: "삼성")
- **Response 200**
```json
{ "success": true, "data": [
  { "code": "005930", "name": "삼성전자", "market": "KOSPI" }
] }
```

#### `GET /stocks/{code}`
- **인증**: Public
- **설명**: 종목 현재가/등락률 + 관련 뉴스 이슈
- **Response 200**
```json
{
  "success": true,
  "data": {
    "code": "005930",
    "name": "삼성전자",
    "current_price": 71800,
    "change_rate": 1.27,
    "change_direction": "UP",
    "price_history_7d": [70200, 70500, 71100, 70900, 71300, 71500, 71800],
    "related_issues": [
      { "id": 501, "title": "HBM 공급계약 확대 기대감에 반도체 업종 강세" }
    ]
  }
}
```

#### `GET /stocks/{code}/news`
- **인증**: Public
- **설명**: 특정 종목 관련 뉴스만 필터링한 리스트 (이미지의 "관심 종목 영향" 카드 클릭 시 진입)
- **Query**: `cursor`, `limit`

#### `GET /users/me/watchlist/market-impact`
- **인증**: Required
- **설명**: 로그인 사용자의 관심 종목들에 대한 "오늘의 영향" 카드 (이미지 우측 상단 패널)
- **Response 200**
```json
{ "success": true, "data": [
  {
    "stock": { "code": "005930", "name": "삼성전자" },
    "related_issue_summary": "HBM 공급계약 이슈",
    "current_price": 71800,
    "change_rate": 1.27,
    "change_direction": "UP",
    "sparkline_7d": [70200, 70500, 71100, 70900, 71300, 71500, 71800]
  }
] }
```

---

### 6.6 교통 (Commute)

#### `POST /commute/check`
- **인증**: Optional
- **설명**: 출발지·도착지 일회성(또는 등록된 기본 경로) 교통 확인. 비로그인은 매번 주소 입력, 로그인 사용자가 `use_default: true`를 보내면 등록된 집/회사 경로 사용.
- **Request Body**
```json
{
  "origin_address": "서울시 ...",
  "destination_address": "분당구 ...",
  "use_default": false
}
```
- **Response 200**
```json
{
  "success": true,
  "data": {
    "origin": { "label": "집", "lat": 37.50, "lng": 127.03 },
    "destination": { "label": "회사", "lat": 37.38, "lng": 127.11 },
    "estimated_minutes": 53,
    "delay_minutes": 12,
    "delay_reason": "분당수서로 사고로 평소보다 12분 더 걸려요",
    "recommended_departure_time": "08:10",
    "route_polyline": "encoded_polyline_string..."
  }
}
```

#### `GET /users/me/commute-routes`
- **인증**: Required
- **설명**: 등록된 집/회사 경로 목록

#### `POST /users/me/commute-routes`
- **인증**: Required
- **설명**: 집/회사 주소 등록 (label: HOME/WORK)
- **Request Body**: `{ "label": "HOME", "address": "...", "latitude": 37.50, "longitude": 127.03 }`

#### `PUT /users/me/commute-routes/{route_id}`
- **인증**: Required
- **설명**: 등록 경로 수정

#### `DELETE /users/me/commute-routes/{route_id}`
- **인증**: Required

---

### 6.7 관심 키워드/종목 (Interest)

#### `GET /interests` 
- **인증**: Optional
- **설명**: 현재 선택된 관심 키워드/종목 목록. 로그인 시 `user_interests`, 비로그인 시 `X-Guest-Session-Id` 기반 `guest_interests` 조회.
- **Response 200**
```json
{ "success": true, "data": [
  { "id": 12, "type": "STOCK", "value": "삼성전자" },
  { "id": 13, "type": "KEYWORD", "value": "HBM" }
] }
```

#### `POST /interests`
- **인증**: Optional
- **설명**: 관심 키워드/종목 추가. 비로그인은 게스트 세션에 TTL 24시간으로 임시 저장 + **추가 시 비동기로 해당 키워드 임베딩 생성**(`interest_embeddings`)하여 다음 브리핑 조회 시 RAG에 반영.
- **Request Body**: `{ "type": "KEYWORD", "value": "AI" }`
- **Response 201**
- **비로그인 응답 헤더**: `X-Guest-Session-Id: {uuid}` (최초 호출 시 발급)
- **Error**: 409 `CONFLICT` (이미 등록된 항목)

#### `DELETE /interests/{interest_id}`
- **인증**: Optional
- **설명**: 관심 항목 삭제 (소유자 확인: 로그인 유저면 user_id, 비로그인이면 세션 토큰 일치 여부 확인 → 불일치 시 403)

#### `POST /interests/migrate`
- **인증**: Required
- **설명**: 비로그인 상태에서 선택했던 임시 관심사를 로그인 직후 영구 계정으로 이전. 클라이언트가 보유 중인 `X-Guest-Session-Id`를 바디로 전달.
- **Request Body**: `{ "guest_session_id": "uuid-string" }`
- **Response 200**: 이전된 항목 개수 반환
```json
{ "success": true, "data": { "migrated_count": 3 } }
```

---

### 6.8 일정 (Schedule)

#### `GET /schedules/today`
- **인증**: Optional
- **설명**: 오늘의 일정 — 시스템 공통 일정(증시개장, 경제지표 발표) + 로그인 시 사용자 일정(예상 퇴근) 병합
- **Response 200**
```json
{ "success": true, "data": [
  { "id": 1, "time": "09:00", "title": "국내 증시 개장", "category": "MARKET" },
  { "id": 2, "time": "15:30", "title": "미국 물가 발표", "category": "ECONOMIC" },
  { "id": 3, "time": "18:20", "title": "예상 퇴근", "category": "COMMUTE" }
] }
```

#### `POST /users/me/schedules`
- **인증**: Required
- **설명**: 사용자 커스텀 일정 추가

#### `DELETE /users/me/schedules/{schedule_id}`
- **인증**: Required

---

### 6.9 사용자/설정 (User)

#### `GET /users/me`
- **인증**: Required
- **Response 200**: 프로필, 가입일, provider 등

#### `PATCH /users/me`
- **인증**: Required
- **설명**: 닉네임 등 프로필 수정

#### `GET /users/me/preferences`
- **인증**: Required
- **설명**: 브리핑 알림 시간, 푸시 on/off 등 설정 화면용

#### `PUT /users/me/preferences`
- **인증**: Required
- **Request Body**: `{ "morning_briefing_time": "07:00", "push_enabled": true }`

---
## 7. RAG 파이프라인 상세 설계

이 프로젝트의 핵심 학습 포인트이므로 별도 섹션으로 상세화한다.

### 7.1 뉴스 중복 제거 (Embedding 기반 클러스터링)

```python
# 개념 흐름 (services/news_dedup_service.py)
def process_new_article(article: RawArticle):
    embedding = openai_client.embed(article.title + article.content_snippet)
    save_to_pgvector(article.id, embedding)

    # 최근 24시간 내 활성 클러스터 중 코사인 유사도 top-1 탐색
    similar_cluster = pgvector_query(
        "SELECT id, 1 - (centroid_embedding <=> %s) AS similarity "
        "FROM issue_clusters WHERE is_active = true "
        "ORDER BY centroid_embedding <=> %s LIMIT 1",
        embedding, embedding
    )

    if similar_cluster and similar_cluster.similarity >= 0.85:   # threshold는 튜닝 필요
        attach_article_to_cluster(article, similar_cluster.id)
        recompute_centroid(similar_cluster.id)   # 클러스터 내 임베딩 평균 갱신
    else:
        create_new_cluster(article)
```
- **threshold(0.85)**: 처음엔 보수적으로 잡고, 실제 한국어 뉴스 임베딩 분포를 보며 조정 권장(같은 사건 다른 기사끼리 0.8~0.9대에 몰리는 경우가 많음).
- 클러스터 기사 수가 **3건 이상**이면 LLM 요약 트리거 (`tasks_news_dedup.py` 내 후속 단계).

### 7.2 이슈 요약 (LLM)

```
프롬프트 설계 (services/rag_service.py):

System: 너는 한국 금융/경제 뉴스를 요약하는 애널리스트야.
        아래 기사 제목들을 보고 핵심 이슈를 한 문장(25자 내외 헤드라인)과
        2~3문장 요약으로 정리해. 과장된 표현 없이 사실 기반으로.

User: [기사1 제목], [기사2 제목], ... (클러스터 내 전체 기사 제목, 최대 20개)

Output: { "headline": "...", "summary": "...", "category": "반도체|금리|AI|...", "related_stocks": ["삼성전자", "SK하이닉스"] }
```
- Output은 JSON mode(`response_format: json_object`)로 강제하여 파싱 안정성 확보.

### 7.3 개인화 브리핑 생성 (RAG 본체)

```
1. Retrieval
   - 사용자의 interest_embeddings (관심 키워드 임베딩들) 각각에 대해
     issue_clusters.centroid_embedding과 코사인 유사도 top-3 클러스터 검색
   - 사용자가 등록한 관심 종목(user_interests type=STOCK)은
     issue_clusters.related_stock_codes 매핑으로 직접 필터링 (벡터 검색 + 정형 필터 혼합)

2. Augmentation (프롬프트 조립)
   System: 너는 사용자의 출퇴근길에 짧은 브리핑을 들려주는 비서야.
           아래 공통 브리핑 베이스와, 사용자가 관심 있어할 이슈들을 참고해서
           "오늘 나에게 중요한 변화 3가지"를 사용자 관점으로 다시 골라줘.

   User:
     [공통 브리핑 텍스트]
     [사용자 관심사: HBM, 삼성전자, AI]
     [retrieval된 관련 이슈 3~5개의 요약]

3. Generation
   - LLM이 "오늘 나에게 중요한 변화 3가지" + 한 줄 헤드라인 재구성
   - 결과를 user_briefings에 캐싱 (재요청 시 재생성하지 않고 캐시 반환, TTL=다음 생성 주기까지)
```

### 7.4 RAG 설계에서 의도적으로 단순화한 부분 (학습 단계 고려)
- Re-ranking 모델(cross-encoder)은 1차 버전에서 생략 — 코사인 유사도 top-k만 사용. 추후 검색 품질 이슈 생기면 추가 학습 포인트로 남겨둠.
- Chunking 전략은 뉴스 제목+스니펫 단위로 고정 — 본문 전체를 다루게 되면 RecursiveCharacterTextSplitter 등 도입 검토.

---

## 8. 비동기 작업 (Celery Beat 스케줄)

| 작업 | 주기 | 설명 |
|---|---|---|
| `collect_news` | 10분 | 네이버뉴스 API/RSS 수집 → `raw_articles` insert |
| `dedup_and_cluster` | 10분 (수집 직후) | 신규 기사 임베딩 + 클러스터링 |
| `summarize_clusters` | 10분 (클러스터링 직후) | 기사 3건 이상 모인 신규/갱신 클러스터 LLM 요약 |
| `generate_daily_briefing` | 1일 2회 (06:00, 17:00) | 공통 브리핑 생성 |
| `generate_user_briefings` | 1일 2회 (06:00, 17:00) | 활성 사용자별 개인화 브리핑 생성 (배치, 로그인 사용자만) |
| `refresh_stock_prices` | 1분 (장중) | 관심 종목 시세 캐시 갱신 |
| `cleanup_expired_guest_interests` | 1시간 | TTL 만료된 게스트 관심사 삭제 |

> **참고**: `generate_user_briefings`를 전체 배치로 돌리되, 신규 가입자나 관심사를 막 바꾼 사용자는 `/briefings/today` 호출 시 캐시가 없으면 **온디맨드로 즉시 1회 생성**하는 fallback 로직을 `briefing_service.py`에 둔다 (사용자가 "방금 키워드 추가했는데 왜 안 바뀌지" 하는 경험 방지).

---

## 9. 개발 착수 순서 제안

학습 목적을 고려해 다음 순서를 권장한다 — RAG가 핵심이므로 너무 늦게 만나지 않게 배치했다.

1. **기반 구축**: FastAPI 프로젝트 스캐폴딩, PostgreSQL+pgvector Docker 구성, 모델/마이그레이션
2. **인증**: 소셜 로그인 + JWT (이후 모든 기능이 Optional Auth를 깔고 가므로 먼저 완성)
3. **외부 연동(읽기 전용 기능 먼저)**: 종목 검색/시세, 교통조회, 날씨 — RAG 없이도 동작하는 기능으로 빠른 성취감 + 외부 API 연동 패턴 학습
4. **뉴스 수집 파이프라인**: 수집 → 저장까지 (아직 임베딩 전)
5. **임베딩 + 중복제거(RAG 1단계: Indexing)**: pgvector 연동, 클러스터링 로직 — 여기서부터 본격 AI 스택 학습
6. **이슈 요약(LLM 활용 1)**: JSON mode 프롬프트 엔지니어링
7. **공통 브리핑 생성**: 비로그인 사용자도 쓸 수 있는 핵심 기능 완성
8. **관심 키워드/종목(Optional Auth + 게스트 세션)**: 비로그인↔로그인 전환(`/interests/migrate`) 포함
9. **개인화 브리핑(RAG 2단계: Retrieval + Generation)**: 전체 RAG 파이프라인 완성 — 프로젝트의 핵심 목표 달성 지점
10. **브리핑 공유, 일정, 설정**: 마무리 기능

---

## 10. 부록

### 10.1 환경변수 (.env.example)
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/gwiteem
REDIS_URL=redis://localhost:6379/0

OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

JWT_SECRET_KEY=...
JWT_ACCESS_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_DAYS=14

KAKAO_CLIENT_ID=...
KAKAO_CLIENT_SECRET=...
NAVER_CLIENT_ID=...
NAVER_CLIENT_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

NAVER_NEWS_API_CLIENT_ID=...
NAVER_NEWS_API_CLIENT_SECRET=...
STOCK_PRICE_API_KEY=...
MAP_DIRECTIONS_API_KEY=...
WEATHER_API_KEY=...

GUEST_SESSION_TTL_HOURS=24
NEWS_CLUSTER_SIMILARITY_THRESHOLD=0.85
```

### 10.2 주요 패키지 (requirements.txt 핵심)
```
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
alembic
pgvector
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
httpx
celery
redis
openai
```

### 10.3 향후 확장 고려 사항 (설계서 범위 밖, 메모만)
- 트래픽 증가 시 pgvector → Qdrant 마이그레이션 (인터페이스를 `repositories/news_repo.py`에 추상화해두면 교체 용이)
- 임베딩 모델을 한국어 특화 오픈소스(`bge-m3`, `ko-sroberta`)로 교체해 비용 절감
- 브리핑 생성 LLM 응답에 대한 평가(RAGAS 등 RAG 평가 프레임워크) 도입
- 알림(FCM Push)을 통한 브리핑 도착 알림

---
*본 문서는 v1 설계서이며, 실제 외부 API(증권사 API 약관, 지도 API 정책 등) 확인 후 세부 스펙은 조정이 필요합니다.*
