from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
import uuid
from app.models.centre import DiagnosticCentre, DiagnosticTest
from app.schemas.centre import DiagnosticCentreCreate, DiagnosticCentreUpdate

async def get_all_centres(db: AsyncSession):
    result = await db.execute(select(DiagnosticCentre))
    return result.scalars().all()

async def get_centre(db: AsyncSession, centre_id: uuid.UUID):
    result = await db.execute(
        select(DiagnosticCentre).options(selectinload(DiagnosticCentre.tests)).where(DiagnosticCentre.id == centre_id)
    )
    centre = result.scalar_one_or_none()
    if not centre:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre

async def create_centre(db: AsyncSession, centre_in: DiagnosticCentreCreate):
    centre = DiagnosticCentre(**centre_in.model_dump())
    db.add(centre)
    await db.commit()
    await db.refresh(centre)
    return centre

async def update_centre(db: AsyncSession, centre_id: uuid.UUID, centre_in: DiagnosticCentreUpdate):
    centre = await get_centre(db, centre_id)
    update_data = centre_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(centre, key, value)
    await db.commit()
    await db.refresh(centre)
    return centre

async def delete_centre(db: AsyncSession, centre_id: uuid.UUID):
    centre = await get_centre(db, centre_id)
    await db.delete(centre)
    await db.commit()
    return {"message": "Centre deleted successfully"}

async def add_test_to_centre(db: AsyncSession, centre_id: uuid.UUID, test_id: uuid.UUID):
    centre = await get_centre(db, centre_id)
    
    test_result = await db.execute(select(DiagnosticTest).where(DiagnosticTest.id == test_id))
    test = test_result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test in centre.tests:
        raise HTTPException(status_code=400, detail="Test already available at this centre")
        
    centre.tests.append(test)
    await db.commit()
    await db.refresh(centre)
    return centre
