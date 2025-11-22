from uuid import UUID
from fastapi import HTTPException, status

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from config.auth import create_access_token, create_refresh_token, verify_token
from models.user import User
from schemas.user import UserCreate, UserLogin, UserRead, UserUpdate, Token
from schemas.base import ResponseModel
from utils.crypto import hash_password, verify_password


class UserService:

    @staticmethod
    async def create_user(data: UserCreate, session: AsyncSession) -> UserRead:
        hashed_password = hash_password(data.password)
        fullname = User.get_fullname(data)
        username = User.get_username(data)

        payload = data.model_dump(exclude_unset=True)
        payload.pop("password", None)

        user = User(
            **payload,
            username=username,
            fullname=fullname,
            password=hashed_password,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def get_user(id: UUID, session: AsyncSession):
        query = select(User).where(User.id == id)
        result = await session.exec(query)

        user = result.unique().one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No user found"
            )

        return user

    @staticmethod
    async def get_users(session: AsyncSession, limit: int = 10, offset: int = 0):
        query = (
            select(User)
            .order_by(User.username)
            .limit(limit=limit)
            .offset(offset=offset)
        )
        result = await session.exec(query)
        users = result.unique().all()
        count = len(users)

        return ResponseModel(count=count, results=users)

    @staticmethod
    async def update_user(id: UUID, data: UserUpdate, session: AsyncSession):
        user = await UserService.get_user(id=id, session=session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No user found"
            )

        for key, value in data.model_dump().items():
            if value:
                setattr(user, key, value)

        return user

    @staticmethod
    async def delete_user(id: UUID, session: AsyncSession):
        user = await UserService.get_user(id=id, session=session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid user id"
            )

        await session.delete(user)
        await session.commit()

        return {}

    @staticmethod
    async def user_login(data: UserLogin, session: AsyncSession) -> Token:
        query = select(User).where(User.username == data.username)
        result = await session.exec(query)
        user = result.unique().one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email or password",
            )

        valid_pass = verify_password(data.password, user.password)

        if not valid_pass:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email or password",
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        return Token(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def refresh_access_token(refresh_token: str, session: AsyncSession) -> Token:
        user_id = verify_token(refresh_token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await session.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        access_token = create_access_token(data={"sub": str(user.id)})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @staticmethod
    async def verify_token_and_get_user(token: str, session: AsyncSession) -> User:
        user_id = verify_token(token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user
