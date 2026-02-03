from fastapi import APIRouter

from app.accounts.router import router as accounts_router
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.notifications.router import router as notifications_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
