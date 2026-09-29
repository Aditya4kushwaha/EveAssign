from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import uuid
import random
from app.models.payment import Payment, PaymentStatus
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.schemas.payment import PaymentCreate
from sqlalchemy.exc import IntegrityError

async def create_payment(db: AsyncSession, payment_in: PaymentCreate, current_user: User):
    # Check booking exists and user is owner
    booking_result = await db.execute(select(Booking).where(Booking.id == payment_in.booking_id))
    booking = booking_result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this booking")
        
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot initiate payment for booking in {booking.status.value} state")

    # Simulate payment provider call
    # In a real system, we might create a pending payment record, then call stripe, then update.
    # Here we simulate success or failure instantly.
    simulated_success = random.choice([True, False])
    payment_status = PaymentStatus.SUCCESS if simulated_success else PaymentStatus.FAILED
    provider_id = f"sim_pay_{uuid.uuid4().hex[:8]}"

    payment = Payment(
        booking_id=booking.id,
        amount=booking.amount, # Amount strictly from booking
        status=payment_status,
        provider_payment_id=provider_id,
        idempotency_key=payment_in.idempotency_key
    )
    db.add(payment)
    
    # Update booking state based on payment
    if payment_status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED
    
    try:
        await db.commit()
        await db.refresh(payment)
        return payment
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Idempotency key already used for a payment")
