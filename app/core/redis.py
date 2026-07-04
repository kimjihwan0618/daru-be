"""
Redis 클라이언트.
로그인 세션(기기별 refresh token) 관리에 사용한다 - app/services/auth_service.py 참고.
"""
from redis.asyncio import Redis, from_url

from app.core.config import settings

redis_client: Redis = from_url(settings.REDIS_URL, decode_responses=True)
