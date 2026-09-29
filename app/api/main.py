from fastapi import APIRouter
from app.api.routes import auth, centres, tests, bookings, payments, webhooks

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(centres.router, prefix="/centres", tags=["centres"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(webhooks.router, prefix="/payments/webhook", tags=["webhooks"])
