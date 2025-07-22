from uuid import UUID
from pydantic import BaseModel

class User(BaseModel):
    id: UUID
    is_admin: bool = False
