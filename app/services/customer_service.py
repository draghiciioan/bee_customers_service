from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID
import logging
import httpx

from app.core.config import settings

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def _sync_auth_profile(self, user_id: UUID, data: dict) -> None:
        """Propagate updates to the auth service."""
        if not settings.AUTH_SERVICE_URL:
            return

        url = f"{settings.AUTH_SERVICE_URL}/api/users/{user_id}"
        try:
            async with httpx.AsyncClient() as client:
                await client.patch(url, json=data, timeout=2)
        except Exception as exc:
            self.logger.warning(
                "Failed to notify auth service",
                extra={"user_id": str(user_id), "error": str(exc)},
            )

    async def create_customer(
        self, customer: CustomerCreate, trace_id: str
    ) -> Customer:
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
            avatar_url=customer.avatar_url,
        )
        self.db.add(db_customer)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            self.logger.warning(
                "Customer already exists",
                extra={
                    "user_id": str(customer.user_id),
                    "business_id": str(customer.business_id),
                    "trace_id": trace_id,
                },
            )
            raise ValueError("Customer already exists") from exc
        await self.db.refresh(db_customer)

        self.logger.info(
            "Customer created",
            extra={
                "customer_id": str(db_customer.id),
                "business_id": str(db_customer.business_id),
                "trace_id": trace_id,
            },
        )
        from app.services.log_service import send_log

        await send_log(
            "v1.customer.created",
            {
                "customer_id": str(db_customer.id),
                "business_id": str(db_customer.business_id),
            },
            trace_id,
        )

        from app.services.event_publisher import publish_event

        payload = {
            "id": str(db_customer.id),
            "user_id": str(db_customer.user_id),
            "business_id": str(db_customer.business_id),
            "trace_id": trace_id,
        }
        await publish_event("v1.customer.created", payload, trace_id)

        return db_customer

    async def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        """Get a customer by ID."""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalars().first()

    async def get_customers(
        self,
        skip: int = 0,
        limit: int = 100,
        business_id: Optional[UUID] = None,
        query: Optional[str] = None,
    ) -> List[Customer]:
        """Return customers filtered by business ID and optional query string."""
        stmt = select(Customer)

        if business_id:
            stmt = stmt.where(Customer.business_id == business_id)

        if query:
            stmt = stmt.where(
                or_(
                    Customer.full_name.ilike(f"%{query}%"),
                    Customer.email.ilike(f"%{query}%"),
                    Customer.phone.ilike(f"%{query}%"),
                )
            )

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_customer(
        self, customer_id: UUID, customer_data: CustomerUpdate, trace_id: str
    ) -> Optional[Customer]:
        """
        Update a customer's information.
        """
        db_customer = await self.get_customer(customer_id)
        if not db_customer:
            return None

        # Update only the fields that are provided
        update_data = customer_data.model_dump(exclude_unset=True)

        # Handle gender enum conversion
        if "gender" in update_data and update_data["gender"] is not None:
            update_data["gender"] = update_data["gender"].value

        fields_changed = []
        for key, value in update_data.items():
            if getattr(db_customer, key) != value:
                setattr(db_customer, key, value)
                fields_changed.append(key)

        await self.db.commit()
        await self.db.refresh(db_customer)

        if fields_changed:
            from app.services.event_publisher import publish_event

            payload = {
                "id": str(db_customer.id),
                "fields_changed": fields_changed,
                "trace_id": trace_id,
            }
            await publish_event("v1.customer.updated", payload, trace_id)

        if fields_changed:
            self.logger.info(
                "Customer updated",
                extra={
                    "customer_id": str(db_customer.id),
                    "fields_changed": fields_changed,
                    "trace_id": trace_id,
                },
            )
            from app.services.log_service import send_log

            await send_log(
                "v1.customer.updated",
                {"customer_id": str(db_customer.id), "fields_changed": fields_changed},
                trace_id,
            )

            auth_fields = {
                field: getattr(db_customer, field)
                for field in ("email", "phone")
                if field in fields_changed
            }
            if auth_fields:
                await self._sync_auth_profile(db_customer.user_id, auth_fields)

        return db_customer

    async def delete_customer(self, customer_id: UUID) -> bool:
        """
        Delete a customer.
        """
        db_customer = await self.get_customer(customer_id)
        if not db_customer:
            return False

        await self.db.delete(db_customer)
        await self.db.commit()
        return True

    async def update_avatar(self, customer_id: UUID, avatar_url: str) -> Optional[Customer]:
        """Update avatar URL for a customer."""
        db_customer = await self.get_customer(customer_id)
        if not db_customer:
            return None

        db_customer.avatar_url = avatar_url
        await self.db.commit()
        await self.db.refresh(db_customer)
        return db_customer
