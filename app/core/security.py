"""
JWT access/refresh 토큰 발급·검증 유틸.

설계서 6.1 인증 흐름 참고:
- access_token: 단기(기본 30분), 모든 Required/Optional Auth 요청에 사용
- refresh_token: 장기(기본 14일), /auth/refresh 에서만 사용. jti(세션 id)를 포함하며
  Redis에 기기(세션) 단위로 등록/삭제된다 - app/services/auth_service.py 참고.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """소셜 로그인만 쓸 경우 비밀번호가 필요 없을 수 있지만,
    추후 자체 로그인(이메일/비번) 확장을 고려해 유틸은 남겨둔다."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, expires_delta: timedelta, token_type: str, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _create_token(
        subject=str(user_id),
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(user_id: int) -> tuple[str, str]:
    """refresh_token과 jti(세션 식별자)를 함께 반환. jti는 Redis 세션 키로 사용된다."""
    jti = uuid.uuid4().hex
    token = _create_token(
        subject=str(user_id),
        expires_delta=timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
        token_type="refresh",
        extra_claims={"jti": jti},
    )
    return token, jti


def decode_token(token: str) -> dict[str, Any] | None:
    """디코딩 실패(만료/위조 등) 시 None 반환. 호출부에서 401 처리."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
