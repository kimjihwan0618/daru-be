"""
AWS SES 이메일 발송 클라이언트. 회원가입/비밀번호 재설정 인증번호 발송에 사용한다.
"""
import asyncio

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.core.exceptions import InvalidRequestException

_ses_client = boto3.client(
    "ses",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
)


def _build_code_email_html(title: str, description: str, code: str) -> str:
    return f"""\
<div style="background-color:#f4f5f7;padding:40px 0;font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif;">
  <div style="max-width:420px;margin:0 auto;background-color:#ffffff;border-radius:8px;overflow:hidden;border:1px solid #e5e7eb;">
    <div style="background-color:#111827;padding:20px 32px;">
      <span style="color:#ffffff;font-size:18px;font-weight:700;">{settings.APP_NAME}</span>
    </div>
    <div style="padding:32px;">
      <p style="margin:0 0 8px;color:#111827;font-size:16px;">{title}</p>
      <p style="margin:0 0 24px;color:#6b7280;font-size:13px;">{description}</p>
      <div style="background-color:#f4f5f7;border-radius:6px;padding:16px;text-align:center;margin-bottom:24px;">
        <span style="font-size:32px;font-weight:700;letter-spacing:6px;color:#111827;">{code}</span>
      </div>
      <p style="margin:0;color:#9ca3af;font-size:12px;">인증번호는 발급 후 {settings.EMAIL_VERIFICATION_CODE_TTL_MINUTES}분간 유효합니다.</p>
      <p style="margin:4px 0 0;color:#9ca3af;font-size:12px;">본인이 요청하지 않았다면 이 메일을 무시하셔도 됩니다.</p>
    </div>
  </div>
</div>"""


def _send_code_email_sync(to_email: str, subject: str, title: str, description: str, code: str) -> None:
    try:
        _ses_client.send_email(
            Source=settings.SES_SENDER_EMAIL,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {
                        "Data": f"인증번호는 {code} 입니다. {settings.EMAIL_VERIFICATION_CODE_TTL_MINUTES}분 이내에 입력해주세요.",
                        "Charset": "UTF-8",
                    },
                    "Html": {
                        "Data": _build_code_email_html(title, description, code),
                        "Charset": "UTF-8",
                    },
                },
            },
        )
    except (ClientError, BotoCoreError) as e:
        raise InvalidRequestException(f"이메일 발송에 실패했습니다: {e}")


async def send_verification_email(to_email: str, code: str) -> None:
    """회원가입용 인증번호 메일 발송. boto3는 동기 클라이언트이므로 스레드로 위임한다."""
    await asyncio.to_thread(
        _send_code_email_sync,
        to_email,
        f"[{settings.APP_NAME}] 이메일 인증번호",
        "이메일 인증번호",
        "아래 인증번호를 회원가입 화면에 입력해주세요.",
        code,
    )


async def send_password_reset_email(to_email: str, code: str) -> None:
    """비밀번호 재설정용 인증번호 메일 발송."""
    await asyncio.to_thread(
        _send_code_email_sync,
        to_email,
        f"[{settings.APP_NAME}] 비밀번호 재설정 인증번호",
        "비밀번호 재설정 인증번호",
        "아래 인증번호를 비밀번호 재설정 화면에 입력해주세요.",
        code,
    )
