from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db import get_session
from services.user import UserService
from config.dependencies import get_current_user
from models.user import User
from schemas.user import UserLogin, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(data: UserLogin, session: AsyncSession = Depends(get_session)):
    """User login endpoint"""
    return await UserService.user_login(data, session)


@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str, session: AsyncSession = Depends(get_session)):
    """Refresh access token using refresh token"""
    return await UserService.refresh_access_token(refresh_token, session)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
    }
