from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from app.models.payment import PaymentStatus

class PaymentCreate(BaseModel):
    booking_id: uuid.UUID
    idempotency_key: str = Field(..., description="Unique key to prevent duplicate payments")

class PaymentResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    amount: float
    status: PaymentStatus
    provider_payment_id: str | None
    idempotency_key: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
