from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.webhook import WebhookEvent
from app.models.payment import Payment, PaymentStatus
from app.models.booking import Booking, BookingStatus
from app.schemas.webhook import WebhookEventPayload
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

async def process_webhook(db: AsyncSession, payload: WebhookEventPayload):
    # Idempotency check via unique event_id
    # We attempt to insert the event. If it fails due to unique constraint, we know it's a duplicate.
    event = WebhookEvent(
        event_id=payload.event_id,
        payment_id=payload.payment_id,
        event_type="payment_update",
        status=payload.status
    )
    
    db.add(event)
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        logger.info(f"Duplicate webhook received for event_id: {payload.event_id}")
        return {"message": "Webhook already processed"}
    
    # Process the actual payment update
    # In reality this might be fetched via provider_payment_id, but we use ID or booking ID here
    # Since the requirements say "event_id, payment_id, booking_id, status", we update the booking
    booking_result = await db.execute(select(Booking).where(Booking.id == payload.booking_id))
    booking = booking_result.scalar_one_or_none()
    
    if not booking:
        # If booking doesn't exist, we might just log it and return 200 so provider stops retrying
        logger.error(f"Booking {payload.booking_id} not found for webhook event {payload.event_id}")
        return {"message": "Webhook processed, but booking not found"}

    if payload.status == "SUCCESS" and booking.status != BookingStatus.CONFIRMED:
        booking.status = BookingStatus.CONFIRMED
        
        # We should also update or create a payment record
        # Finding payment by provider_payment_id if it exists
        payment_res = await db.execute(select(Payment).where(Payment.provider_payment_id == payload.payment_id))
        payment = payment_res.scalar_one_or_none()
        
        if payment:
            payment.status = PaymentStatus.SUCCESS
        else:
            # Create if it didn't exist (e.g. out of band payment)
            payment = Payment(
                booking_id=booking.id,
                amount=booking.amount,
                status=PaymentStatus.SUCCESS,
                provider_payment_id=payload.payment_id,
                idempotency_key=f"webhook_{payload.event_id}"
            )
            db.add(payment)
            
        await db.commit()

    elif payload.status == "FAILED" and booking.status != BookingStatus.FAILED:
        booking.status = BookingStatus.FAILED
        
        payment_res = await db.execute(select(Payment).where(Payment.provider_payment_id == payload.payment_id))
        payment = payment_res.scalar_one_or_none()
        
        if payment:
            payment.status = PaymentStatus.FAILED
        else:
            payment = Payment(
                booking_id=booking.id,
                amount=booking.amount,
                status=PaymentStatus.FAILED,
                provider_payment_id=payload.payment_id,
                idempotency_key=f"webhook_{payload.event_id}"
            )
            db.add(payment)
            
        await db.commit()

    return {"message": "Webhook processed successfully"}
