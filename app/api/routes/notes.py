from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.schemas.note import NoteCreatePayload, NoteResponse
from app.services.note_service import NoteService
from app.api.dependencies import User, require_admin, trace_id_dependency

customer_router = APIRouter()


@customer_router.post(
    "/{customer_id}/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer_note(
    customer_id: UUID,
    note: NoteCreatePayload,
    trace_id: str = Depends(trace_id_dependency),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Create a note for a specific customer."""
    service = NoteService(db)
    return await service.create_customer_note(customer_id, note, trace_id)


@customer_router.get(
    "/{customer_id}/notes",
    response_model=List[NoteResponse],
)
async def get_customer_notes(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Retrieve all notes for a customer."""
    service = NoteService(db)
    return await service.get_notes_by_customer(customer_id)


@customer_router.delete(
    "/{customer_id}/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer_note(
    customer_id: UUID,
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Delete a specific note for a customer."""
    service = NoteService(db)
    success = await service.delete_customer_note(customer_id, note_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return None
