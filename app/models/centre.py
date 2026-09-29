from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from sqlalchemy import Table, Column
from app.db.database import Base

centre_tests = Table(
    "centre_tests",
    Base.metadata,
    Column("centre_id", ForeignKey("diagnostic_centres.id"), primary_key=True),
    Column("test_id", ForeignKey("diagnostic_tests.id"), primary_key=True),
)

class DiagnosticCentre(BaseModel):
    __tablename__ = "diagnostic_centres"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)

    tests = relationship("DiagnosticTest", secondary=centre_tests, back_populates="centres")
    bookings = relationship("Booking", back_populates="centre")

class DiagnosticTest(BaseModel):
    __tablename__ = "diagnostic_tests"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)

    centres = relationship("DiagnosticCentre", secondary=centre_tests, back_populates="tests")
    bookings = relationship("Booking", back_populates="test")
