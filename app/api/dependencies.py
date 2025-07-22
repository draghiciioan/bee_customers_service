from uuid import uuid4

from app.schemas.user import User


def require_customer_or_admin() -> User:
    """Stub dependency that returns a dummy user."""
    return User(id=uuid4(), is_admin=True)
