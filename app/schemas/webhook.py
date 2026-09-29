from pydantic import BaseModel
import uuid

class WebhookEventPayload(BaseModel):
    event_id: str
    payment_id: str
    booking_id: uuid.UUID
    status: str
