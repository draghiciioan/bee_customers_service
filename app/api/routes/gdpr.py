from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.gdpr_service import GDPRService
from app.schemas.gdpr import GDPRRequest
from app.api.dependencies import User, require_customer_or_admin

router = APIRouter()


@router.post("/export", status_code=status.HTTP_200_OK)
def export_customer_data(
    request: GDPRRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_customer_or_admin),
):
    """
    Export all data for a specific customer (GDPR compliance).
    """
    gdpr_service = GDPRService(db)
    data = gdpr_service.export_customer_data(request.user_id, request.business_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return data


@router.post("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_data(
    request: GDPRRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_customer_or_admin),
):
    """
    Delete all data for a specific customer (GDPR compliance).
    """
    gdpr_service = GDPRService(db)
    success = gdpr_service.delete_customer_data(request.user_id, request.business_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return None
