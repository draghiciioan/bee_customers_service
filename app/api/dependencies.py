from app.core.security import (
    get_current_user,
    require_admin,
    require_customer_or_admin,
    require_internal_service,
)
from uuid import uuid4

from fastapi import Request
from app.schemas.user import User


def trace_id_dependency(request: Request) -> str:
    """Return X-Trace-Id header value or generate a new UUID."""
    return request.headers.get("X-Trace-Id", str(uuid4()))

__all__ = [
    "get_current_user",
    "require_admin",
    "require_customer_or_admin",
    "require_internal_service",
    "trace_id_dependency",
    "User",
]
