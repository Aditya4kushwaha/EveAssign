from fastapi import APIRouter, Depends, status
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services import payment_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment_in: PaymentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await payment_service.create_payment(db, payment_in, current_user)
