from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.webhook import WebhookEventPayload
from app.services import webhook_service

router = APIRouter()

@router.post("", status_code=status.HTTP_200_OK)
async def handle_webhook(payload: WebhookEventPayload, db: AsyncSession = Depends(get_db)):
    # Note: No user authentication here. A real system would verify a webhook signature.
    return await webhook_service.process_webhook(db, payload)
