"""
공통 에러 코드 및 예외 클래스.
설계서 5.5 공통 에러 코드 표 기준.

app/main.py 에서 AppException 핸들러를 등록해
{"success": false, "data": null, "error": {"code": ..., "message": ...}} 포맷으로 응답한다.
"""
from fastapi import status


class AppException(Exception):
    """비즈니스 로직에서 의도적으로 발생시키는 예외의 베이스 클래스."""

    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "인증이 필요합니다.", code: str = "UNAUTHORIZED"):
        super().__init__(code=code, message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    def __init__(self, message: str = "권한이 없습니다.", code: str = "FORBIDDEN"):
        super().__init__(code=code, message=message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundException(AppException):
    def __init__(self, message: str = "리소스를 찾을 수 없습니다.", code: str = "NOT_FOUND"):
        super().__init__(code=code, message=message, status_code=status.HTTP_404_NOT_FOUND)


class ConflictException(AppException):
    def __init__(self, message: str = "이미 존재하는 리소스입니다.", code: str = "CONFLICT"):
        super().__init__(code=code, message=message, status_code=status.HTTP_409_CONFLICT)


class InvalidRequestException(AppException):
    def __init__(self, message: str = "요청이 올바르지 않습니다.", code: str = "INVALID_REQUEST"):
        super().__init__(code=code, message=message, status_code=status.HTTP_400_BAD_REQUEST)
