from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi import APIRouter, Depends, status

from config.db import get_session
from config.dependencies import get_current_user
from models.user import User
from schemas.base import ResponseModel
from schemas.user import UserCreate, UserRead, UserUpdate
from services.user import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await UserService.get_user(id=id, session=session)


@router.post("/", response_model=UserRead, status_code=status.HTTP_200_OK)
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await UserService.create_user(data=data, session=session)


@router.get("/", response_model=ResponseModel)
async def get_users(
    username: str | None = None,
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await UserService.get_users(
        username=username, limit=limit, offset=offset, session=session
    )


@router.patch("/{id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(
    id: UUID,
    data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await UserService.update_user(id=id, data=data, session=session)


@router.delete("/", response_model={}, status_code=status.HTTP_200_OK)
async def delete_user(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await UserService.delete_user(id=id, session=session)
