from collections import defaultdict
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import HTTPException, Request, status
from ua_parser.user_agent_parser import Parse

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from config.auth import create_access_token, create_refresh_token, verify_token
from models.user import User
from schemas.user import UserCreate, UserLogin, UserRead, UserUpdate, Token
from schemas.base import ResponseModel
from utils.crypto import hash_password, verify_password

from config.settings import REQUESTS_PER_MINUTE


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


class UserActivity:
    def __init__(self, requests_per_minute: int = REQUESTS_PER_MINUTE):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.user_info = defaultdict(list)

    async def is_rate_limited(self, token: str) -> bool:
        """Check if token has exceeded rate limit"""
        now = datetime.now()
        minutes_ago = now - timedelta(minutes=1)

        self.requests[token] = [
            req for req in self.requests[token] if req > minutes_ago
        ]

        if len(self.requests[token]) >= self.requests_per_minute:
            return True

        self.requests[token].append(now)
        return False

    async def get_client_ip(self, request: Request):
        forwarded = request.headers.get("X-Forwarded-For")

        if forwarded:
            return forwarded.split(",")[0].strip()

        return request.client.host if request.client else "unknown"

    async def get_device_identifier(self, user_agent: str):
        ua = Parse(user_agent)

        browser = ua["user_agent"]["family"]
        os = ua["os"]["family"]
        device = ua["device"]["family"]

        return f"{browser}_{os}_{device}"

    async def track_user_activity(self, user_id: str, ip: str, device: str):
        current_time = datetime.now()

        activity = {
            "ip": ip,
            "device": device,
            "last_seen": current_time,
            "ip_changed": False,
            "device_changed": False,
            "username": user_id,
        }

        if user_id not in self.user_info:
            self.user_info[user_id] = [activity]
            return True

        user_data = self.user_info[user_id]

        ip_changed = user_data[-1]["ip"] != ip
        device_changed = user_data[-1]["device"] != device

        user_data[-1]["ip_changed"] = ip_changed
        user_data[-1]["ip"] = ip
        user_data[-1]["device_changed"] = device_changed
        user_data[-1]["last_seen"] = current_time
        user_data[-1]["device"] = device
        user_data[-1]["username"] = user_id

        return user_data
