"""
소셜 로그인(카카오/네이버/구글) OAuth 클라이언트.

TODO(구현 필요) - 각 provider별 흐름:

[카카오]
1. authorize URL: https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=code
2. 토큰 교환: POST https://kauth.kakao.com/oauth/token
3. 사용자 정보: GET https://kapi.kakao.com/v2/user/me (Authorization: Bearer {access_token})

[네이버]
1. authorize URL: https://nid.naver.com/oauth2.0/authorize?...
2. 토큰 교환: GET https://nid.naver.com/oauth2.0/token
3. 사용자 정보: GET https://openapi.naver.com/v1/nid/me

[구글]
1. authorize URL: https://accounts.google.com/o/oauth2/v2/auth?...
2. 토큰 교환: POST https://oauth2.googleapis.com/token
3. 사용자 정보: GET https://www.googleapis.com/oauth2/v2/userinfo
"""


def build_authorize_url(provider: str) -> str:
    """TODO(구현 필요): provider별 authorize URL 조립"""
    raise NotImplementedError


async def exchange_code_for_token(provider: str, code: str) -> str:
    """TODO(구현 필요): provider별 토큰 교환 후 access_token 반환"""
    raise NotImplementedError


async def fetch_user_info(provider: str, access_token: str) -> dict:
    """
    TODO(구현 필요): provider별 사용자 정보 조회
    반환 형태 통일 권장: {"provider_id": ..., "email": ..., "nickname": ..., "profile_image_url": ...}
    """
    raise NotImplementedError
