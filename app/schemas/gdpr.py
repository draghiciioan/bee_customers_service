from pydantic import BaseModel
from uuid import UUID


class GDPRRequest(BaseModel):
    """
    Request model for GDPR-related operations (export and deletion).
    """
    user_id: UUID
    business_id: UUID
