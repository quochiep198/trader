from fastapi import APIRouter
from app.api import auth
from app.api import rules
from app.api import trades

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(trades.router, prefix="/trade-check", tags=["trade-check"])

