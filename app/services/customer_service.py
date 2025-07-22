from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from uuid import UUID

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, customer: CustomerCreate) -> Customer:
        """
        Create a new customer in the database.
        """
        db_customer = Customer(
            user_id=customer.user_id,
            business_id=customer.business_id,
            full_name=customer.full_name,
            email=customer.email,
            phone=customer.phone,
            gender=customer.gender.value if customer.gender else None,
            avatar_url=customer.avatar_url
        )
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        """
        Get a customer by ID.
        """
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_customers(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        business_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> List[Customer]:
        """
        Get all customers with optional filtering.
        """
        query = self.db.query(Customer)
        
        if business_id:
            query = query.filter(Customer.business_id == business_id)
            
        if search:
            query = query.filter(
                or_(
                    Customer.full_name.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%")
                )
            )
            
        return query.offset(skip).limit(limit).all()

    def update_customer(self, customer_id: UUID, customer_data: CustomerUpdate) -> Optional[Customer]:
        """
        Update a customer's information.
        """
        db_customer = self.get_customer(customer_id)
        if not db_customer:
            return None
            
        # Update only the fields that are provided
        update_data = customer_data.dict(exclude_unset=True)
        
        # Handle gender enum conversion
        if "gender" in update_data and update_data["gender"] is not None:
            update_data["gender"] = update_data["gender"].value
            
        for key, value in update_data.items():
            setattr(db_customer, key, value)
            
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def delete_customer(self, customer_id: UUID) -> bool:
        """
        Delete a customer.
        """
        db_customer = self.get_customer(customer_id)
        if not db_customer:
            return False
            
        self.db.delete(db_customer)
        self.db.commit()
        return True
