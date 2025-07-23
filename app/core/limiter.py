from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def rate_limit_key(request: Request) -> str:
    """Return user ID from request state or client IP."""
    user = getattr(request.state, "user", None)
    return str(user.id) if user else get_remote_address(request)


limiter = Limiter(key_func=rate_limit_key)
