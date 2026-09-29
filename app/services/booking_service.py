from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import uuid
from app.models.booking import Booking, BookingStatus
from app.models.centre import DiagnosticCentre, DiagnosticTest
from app.models.user import User, RoleEnum
from app.schemas.booking import BookingCreate

async def create_booking(db: AsyncSession, booking_in: BookingCreate, current_user: User):
    # Verify centre exists
    centre_result = await db.execute(select(DiagnosticCentre).where(DiagnosticCentre.id == booking_in.centre_id))
    centre = centre_result.scalar_one_or_none()
    if not centre:
        raise HTTPException(status_code=404, detail="Centre not found")

    # Verify test exists
    test_result = await db.execute(select(DiagnosticTest).where(DiagnosticTest.id == booking_in.test_id))
    test = test_result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # Verify test is available at the centre
    centre_with_tests_result = await db.execute(
        select(DiagnosticCentre).options(
            select.orm.selectinload(DiagnosticCentre.tests)
        ).where(DiagnosticCentre.id == booking_in.centre_id)
    )
    centre_with_tests = centre_with_tests_result.scalar_one_or_none()
    if not any(t.id == test.id for t in centre_with_tests.tests):
        raise HTTPException(status_code=400, detail="Test is not available at this centre")

    booking = Booking(
        user_id=current_user.id,
        centre_id=booking_in.centre_id,
        test_id=booking_in.test_id,
        appointment_date_time=booking_in.appointment_date_time.isoformat(),
        amount=test.price, # Set securely from DB
        status=BookingStatus.PENDING
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking

async def get_all_bookings(db: AsyncSession, current_user: User):
    if current_user.role == RoleEnum.ADMIN:
        result = await db.execute(select(Booking))
    else:
        result = await db.execute(select(Booking).where(Booking.user_id == current_user.id))
    return result.scalars().all()

async def get_booking(db: AsyncSession, booking_id: uuid.UUID, current_user: User):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if current_user.role != RoleEnum.ADMIN and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this booking")
        
    return booking

async def cancel_booking(db: AsyncSession, booking_id: uuid.UUID, current_user: User):
    booking = await get_booking(db, booking_id, current_user)
    
    if booking.status in [BookingStatus.CONFIRMED, BookingStatus.FAILED, BookingStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel a booking in {booking.status.value} state")
        
    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)
    return booking
