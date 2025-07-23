from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.schemas.user import User


bearer_scheme = HTTPBearer()


def decode_jwt(token: str) -> dict:
    """Decode a JWT token using the project secret key."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from exc


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    """Return the current user extracted from the Authorization header."""
    payload = decode_jwt(credentials.credentials)
    try:
        user_id = UUID(payload.get("sub"))
    except Exception as exc:  # pragma: no cover - sanity check
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload") from exc
    role = payload.get("role", "customer")
    is_admin = role.startswith("admin")
    user = User(id=user_id, is_admin=is_admin, role=role)
    request.state.user = user
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user has an administrator role."""
    if not current_user.role.startswith("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


def require_customer_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Allow access only to admin or customer roles."""
    if not (current_user.role.startswith("admin") or current_user.role == "customer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer or admin role required",
        )
    return current_user


def require_internal_service(current_user: User = Depends(get_current_user)) -> User:
    """Allow only tokens issued for internal services."""
    if current_user.role != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Internal service only")
    return current_user
