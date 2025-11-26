from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from config.db import get_session
from config.dependencies import get_current_user
from models.user import User
from schemas.base import ResponseModel
from schemas.period_year import PeriodRead
from services.period_year import PeriodService


router = APIRouter(prefix="/period", tags=["periods"])


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_periods(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    period_year_id: int | None = None,
    period_code: str | None = None,
    period_name: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    return await PeriodService.get_periods(
        session=session,
        period_year_id=period_year_id,
        period_code=period_code,
        period_name=period_name,
        limit=limit,
        offset=offset,
    )


@router.get("/{id}", response_model=PeriodRead, status_code=status.HTTP_200_OK)
async def get_period(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await PeriodService.get_period(id=id, session=session)
