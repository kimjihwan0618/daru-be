"""
소셜 로그인(카카오/네이버/구글) OAuth 클라이언트.
"""
import httpx

from app.core.config import settings
from app.core.exceptions import InvalidRequestException

SUPPORTED_PROVIDERS = {"naver", "google"}  # TODO(구현 필요): kakao email 미제공 이슈 해결 후 재활성화


def _assert_provider(provider: str) -> None:
    if provider not in SUPPORTED_PROVIDERS:
        raise InvalidRequestException(f"지원하지 않는 provider입니다: {provider}")


def build_authorize_url(provider: str) -> str:
    """provider별 OAuth authorize URL 반환."""
    _assert_provider(provider)

    # TODO(구현 필요): kakao email 미제공 이슈 해결 전까지 비활성화 (SUPPORTED_PROVIDERS에서도 제외됨)
    # if provider == "kakao":
    #     return (
    #         "https://kauth.kakao.com/oauth/authorize"
    #         f"?client_id={settings.KAKAO_CLIENT_ID}"
    #         f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
    #         "&response_type=code"
    #     )
    if provider == "naver":
        return (
            "https://nid.naver.com/oauth2.0/authorize"
            f"?client_id={settings.NAVER_CLIENT_ID}"
            f"&redirect_uri={settings.NAVER_REDIRECT_URI}"
            "&response_type=code"
            "&state=gwiteem"
        )
    # google
    return (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
    )


async def exchange_code_for_token(provider: str, code: str) -> str:
    """provider에 code를 넘겨 OAuth access_token을 교환해 반환."""
    _assert_provider(provider)

    async with httpx.AsyncClient() as client:
        # TODO(구현 필요): kakao email 미제공 이슈 해결 전까지 비활성화 (SUPPORTED_PROVIDERS에서도 제외됨)
        # if provider == "kakao":
        #     resp = await client.post(
        #         "https://kauth.kakao.com/oauth/token",
        #         data={
        #             "grant_type": "authorization_code",
        #             "client_id": settings.KAKAO_CLIENT_ID,
        #             "client_secret": settings.KAKAO_CLIENT_SECRET,
        #             "redirect_uri": settings.KAKAO_REDIRECT_URI,
        #             "code": code,
        #         },
        #     )
        if provider == "naver":
            resp = await client.get(
                "https://nid.naver.com/oauth2.0/token",
                params={
                    "grant_type": "authorization_code",
                    "client_id": settings.NAVER_CLIENT_ID,
                    "client_secret": settings.NAVER_CLIENT_SECRET,
                    "redirect_uri": settings.NAVER_REDIRECT_URI,
                    "code": code,
                    "state": "gwiteem",
                },
            )
        else:  # google
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "code": code,
                },
            )

    if resp.status_code != 200:
        raise InvalidRequestException(f"OAuth 토큰 교환 실패: {provider}")

    return resp.json()["access_token"]


async def fetch_user_info(provider: str, access_token: str) -> dict:
    """
    provider에서 사용자 정보 조회.
    반환 형태: {"provider_id": str, "email": str|None, "nickname": str, "profile_image_url": str|None}
    """
    _assert_provider(provider)

    async with httpx.AsyncClient() as client:
        # TODO(구현 필요): kakao email 미제공 이슈 해결 전까지 비활성화 (SUPPORTED_PROVIDERS에서도 제외됨)
        # if provider == "kakao":
        #     resp = await client.get(
        #         "https://kapi.kakao.com/v2/user/me",
        #         headers={"Authorization": f"Bearer {access_token}"},
        #     )
        #     resp.raise_for_status()
        #     data = resp.json()
        #     kakao_account = data.get("kakao_account", {})
        #     profile = kakao_account.get("profile", {})
        #     return {
        #         "provider_id": str(data["id"]),
        #         "email": kakao_account.get("email"),
        #         "nickname": profile.get("nickname", "카카오 사용자"),
        #         "profile_image_url": profile.get("profile_image_url"),
        #     }

        if provider == "naver":
            resp = await client.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            data = resp.json().get("response", {})
            return {
                "provider_id": data["id"],
                "email": data.get("email"),
                "nickname": data.get("nickname", "네이버 사용자"),
                "profile_image_url": data.get("profile_image"),
            }

        # google
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "provider_id": data["id"],
            "email": data.get("email"),
            "nickname": data.get("name", "구글 사용자"),
            "profile_image_url": data.get("picture"),
        }
