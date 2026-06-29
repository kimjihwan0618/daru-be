"""
공통 응답 포맷. 설계서 5.4 / 5.5 대응.
{"success": true, "data": {...}, "error": null}
{"success": false, "data": null, "error": {"code": ..., "message": ...}}
"""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    error: ErrorDetail | None = None


class CursorPage(BaseModel, Generic[T]):
    """cursor 기반 페이지네이션 공통 포맷. 설계서 5.6 대응."""

    items: list[T]
    next_cursor: str | None = None
