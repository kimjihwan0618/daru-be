# CLAUDE.md

gwiteem 백엔드 — 출퇴근 맞춤 브리핑 서비스 API (FastAPI, SQLite → PostgreSQL/pgvector 전환 예정).

- 설계 의도: [gwiteem_API_설계서.md](../gwiteem_API_설계서.md)
- 구현 순서 / 전환 체크리스트: [README.md](../README.md)
- 이 문서와 내용이 겹치면 README/설계서가 우선.

뼈대만 생성된 저장소. `services/`, `external/`, `workers/`는 대부분 `NotImplementedError` + `TODO(구현 필요)` 스텁. 작업은 보통 "이 TODO 구현해줘" 형태로 들어옴.

세부 규칙은 `.claude/rules/`에 주제별로 분리되어 있음 (아키텍처, 코드 컨벤션, DB/마이그레이션, 작업 범위).

## 명령어

```bash
uvicorn app.main:app --reload      # http://localhost:8000/docs
alembic revision --autogenerate -m "설명"   # 모델 변경 후 마이그레이션 생성
alembic upgrade head                # 마이그레이션 적용
pytest app/tests/                   # 테스트
```

## 완료 기준

라우터 구현 후 Swagger UI(`/docs`) 또는 실제 요청으로 반드시 동작 확인. `NotImplementedError`가 사라졌는지 확인만으로는 불충분.
