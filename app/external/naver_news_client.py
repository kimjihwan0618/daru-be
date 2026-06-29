"""
네이버 뉴스 검색 API 클라이언트.
문서: https://developers.naver.com/docs/serviceapi/search/news/news.md

TODO(구현 필요):
- httpx.AsyncClient 로 GET https://openapi.naver.com/v1/search/news.json 호출
- 헤더: X-Naver-Client-Id, X-Naver-Client-Secret (settings에서 로드)
- 응답 파싱 -> RawArticle 모델 형태로 변환해 반환
- Rate limit(일일 호출 한도) 고려해 Celery task 주기 설정
"""
import httpx

from app.core.config import settings

NAVER_NEWS_SEARCH_URL = "https://openapi.naver.com/v1/search/news.json"


async def search_news(query: str, display: int = 20, sort: str = "date") -> list[dict]:
    """
    TODO(구현 필요):
        headers = {
            "X-Naver-Client-Id": settings.NAVER_NEWS_API_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_NEWS_API_CLIENT_SECRET,
        }
        params = {"query": query, "display": display, "sort": sort}
        async with httpx.AsyncClient() as client:
            resp = await client.get(NAVER_NEWS_SEARCH_URL, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()["items"]
    """
    raise NotImplementedError
