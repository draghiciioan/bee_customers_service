from uuid import UUID
from pydantic import BaseModel

class User(BaseModel):
    id: UUID
    role: str = "customer"
    is_admin: bool = False
