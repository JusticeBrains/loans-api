from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from config.db import get_session
from models.user import RevokedToken
from services.user import UserService, UserActivity

security = HTTPBearer()

user_activity = UserActivity()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
    request: Request = None,
):
    token = credentials.credentials

    revoked_token = await session.exec(
        select(RevokedToken).where(RevokedToken.token == token)
    )
    revoked_token = revoked_token.one_or_none()

    if revoked_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    if await user_activity.is_rate_limited(token=token):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests"
        )

    user_agent = request.headers.get("User-Agent", "unknown")
    device_identifier = await user_activity.get_device_identifier(user_agent)
    client_ip = await user_activity.get_client_ip(request)

    user = await UserService.verify_token_and_get_user(token, session)

    user_info = await user_activity.track_user_activity(
        user_id=user.username, ip=client_ip, device=device_identifier
    )

    return user
