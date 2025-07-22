from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter()


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new customer profile.
    """
    customer_service = CustomerService(db)
    return customer_service.create_customer(customer)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a customer by ID.
    """
    customer_service = CustomerService(db)
    customer = customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    business_id: Optional[UUID] = None,
    search: Optional[str] = Query(None, min_length=3),
    db: Session = Depends(get_db)
):
    """
    Get all customers with optional filtering by business_id and search term.
    """
    customer_service = CustomerService(db)
    return customer_service.get_customers(skip, limit, business_id, search)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: UUID,
    customer: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a customer's information.
    """
    customer_service = CustomerService(db)
    updated_customer = customer_service.update_customer(customer_id, customer)
    if not updated_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return updated_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a customer.
    """
    customer_service = CustomerService(db)
    success = customer_service.delete_customer(customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return None


@router.get("/{customer_id}/statistics", response_model=dict)
def get_customer_statistics(
    customer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific customer.
    """
    customer_service = CustomerService(db)
    customer = customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return {
        "total_orders": customer.total_orders,
        "total_appointments": customer.total_appointments,
        "last_order_date": customer.last_order_date,
        "last_appointment_date": customer.last_appointment_date,
        "lifetime_value": float(customer.lifetime_value) if customer.lifetime_value else 0.0
    }
