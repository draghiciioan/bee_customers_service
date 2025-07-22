from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class NoteBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)


class NoteCreate(NoteBase):
    customer_id: UUID
    created_by: UUID  # admin user_id


class NoteCreatePayload(NoteBase):
    """Payload for routes where customer_id is passed in the path."""
    created_by: UUID  # admin user_id


class NoteResponse(NoteBase):
    id: UUID
    customer_id: UUID
    created_by: UUID
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
