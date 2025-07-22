from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.customer_note import CustomerNote
from app.schemas.note import NoteCreate, NoteResponse
from app.services.note_service import NoteService

router = APIRouter()


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new note for a customer.
    """
    note_service = NoteService(db)
    return note_service.create_note(note)


@router.get("/customer/{customer_id}", response_model=List[NoteResponse])
def get_customer_notes(
    customer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all notes for a specific customer.
    """
    note_service = NoteService(db)
    return note_service.get_notes_by_customer(customer_id)


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a note by ID.
    """
    note_service = NoteService(db)
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a note.
    """
    note_service = NoteService(db)
    success = note_service.delete_note(note_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return None