from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
import uuid
from app.models.centre import DiagnosticTest
from app.schemas.test import DiagnosticTestCreate, DiagnosticTestUpdate

async def get_all_tests(db: AsyncSession):
    result = await db.execute(select(DiagnosticTest))
    return result.scalars().all()

async def get_test(db: AsyncSession, test_id: uuid.UUID):
    result = await db.execute(select(DiagnosticTest).where(DiagnosticTest.id == test_id))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

async def create_test(db: AsyncSession, test_in: DiagnosticTestCreate):
    test = DiagnosticTest(**test_in.model_dump())
    db.add(test)
    await db.commit()
    await db.refresh(test)
    return test

async def update_test(db: AsyncSession, test_id: uuid.UUID, test_in: DiagnosticTestUpdate):
    test = await get_test(db, test_id)
    update_data = test_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(test, key, value)
    await db.commit()
    await db.refresh(test)
    return test

async def delete_test(db: AsyncSession, test_id: uuid.UUID):
    test = await get_test(db, test_id)
    await db.delete(test)
    await db.commit()
    return {"message": "Test deleted successfully"}
