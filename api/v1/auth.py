from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from config.db import get_session
from services.user import UserService
from config.dependencies import get_current_user
from models.user import RevokedToken, User
from schemas.user import UserLogin, Token

security = HTTPBearer()

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


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials

    revoked = RevokedToken(token=token)
    session.add(revoked)
    await session.commit()

    return {"detail": "Logged out successfully"}
