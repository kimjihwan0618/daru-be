# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소에서 작업할 때 따라야 할 지침입니다.

## 프로젝트 개요

DARU 백엔드 — 출퇴근 맞춤 브리핑 서비스 API (FastAPI, SQLite → PostgreSQL/pgvector 전환 예정).
설계 의도는 [DARU_API_설계서.md](DARU_API_설계서.md), 구현 순서와 전환 체크리스트는 [README.md](README.md)를 따른다. 이 문서와 내용이 겹치면 README/설계서가 우선한다.

이 저장소는 **엔드포인트/모델/스키마 뼈대까지 생성된 상태**이며, 대부분의 `services/`, `external/`, `workers/` 함수는 `raise NotImplementedError`와 `TODO(구현 필요)` 주석만 있는 스텁이다. 작업은 대개 "이 TODO를 구현해줘" 형태로 들어온다.

## 실행 / 검증 명령어

```bash
uvicorn app.main:app --reload      # 서버 실행 (http://localhost:8000/docs)
alembic revision --autogenerate -m "설명"   # 모델 변경 후 마이그레이션 생성
alembic upgrade head                # 마이그레이션 적용
pytest app/tests/                   # 테스트
```

작업을 완료로 보고하기 전에 반드시 해당 라우터를 Swagger UI(`/docs`) 또는 실제 요청으로 호출해 동작을 확인한다. `NotImplementedError`가 사라졌는지 확인하는 것만으로는 부족하다.

## 아키텍처: 계층 의존 규칙

```
routers → services → repositories → models
```

- 라우터는 요청/응답 스키마 검증과 인증(Depends)만 담당한다. **DB 쿼리를 직접 작성하지 않는다.**
- 비즈니스 로직은 `services/`에 작성하고, DB 접근은 반드시 `repositories/`를 거친다.
- `repositories/` 함수는 순수 DB 쿼리 캡슐화만 하고 비즈니스 규칙(권한 체크, 조합 로직)을 넣지 않는다.
- 외부 API 호출은 `services/`가 아니라 `external/*_client.py`에 캡슐화한다.

## 코드 컨벤션

- 함수/모듈 docstring, 주석, 예외 메시지는 한국어로 작성한다 (기존 코드 전체가 한국어).
- 타입힌트 필수. `str | None` 같은 PEP 604 문법 사용 (`Optional[str]` 아님).
- 비동기 SQLAlchemy(`AsyncSession`) + `sqlalchemy.future.select` 패턴을 따른다.
- 아직 구현하지 않은 부분은 `# TODO(구현 필요): ...` 형식 주석으로 남긴다. 이미 있는 TODO를 구현했으면 주석을 지운다.
- 에러는 `app/core/exceptions.py`의 `AppException` 서브클래스(`NotFoundException`, `UnauthorizedException` 등)를 raise한다. FastAPI `HTTPException`을 직접 쓰지 않는다.
- 응답 스키마는 `ApiResponse[T]`(`app/schemas/common.py`)로 감싼다. 목록 응답 중 커서 기반 페이지네이션이 필요하면 `CursorPage[T]`를 사용한다.
- 인증 패턴 3가지를 구분해서 쓴다 (`app/core/deps.py`):
  - Public: Depends 없음
  - Optional: `get_optional_user`
  - Required: `get_current_user`

## 작업 시 주의사항

- 스켈레톤에 이미 정의된 모델/스키마 필드를 임의로 바꾸지 말고, 필요하면 먼저 이유를 설명하고 확인받는다. README 5절("미해결 설계 메모")에 나열된 항목(`users.preferences`, 브리핑 피드백 테이블, 공유 링크 만료 정책 등)은 설계가 보류된 상태이므로 임의로 테이블/컬럼을 추가하기 전에 사용자에게 방향을 확인한다.
- `app/models/news.py`의 임베딩 컬럼은 SQLite 환경에서 임시 타입을 쓰고 있다. pgvector 전환 관련 작업이 아니라면 이 부분을 건드리지 않는다.
- Alembic 마이그레이션은 모델 변경 후 직접 작성하지 말고 `--autogenerate`로 생성한 뒤 검토한다.
- 요청받지 않은 리팩터링, 추상화 추가, 여러 소셜 로그인 동시 구현 등 범위를 넘어서는 작업은 하지 않는다. README의 "구현 우선순위 가이드"(카카오 로그인 → 읽기 전용 기능 → 뉴스 수집 → RAG → 개인화)를 참고해 순서를 벗어난 선행 구현이 필요한지 먼저 확인한다.
