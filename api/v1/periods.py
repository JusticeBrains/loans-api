from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from config.db import get_session
from schemas.base import ResponseModel
from schemas.period_year import PeriodRead
from services.period_year import PeriodService


router = APIRouter(prefix="/period", tags=["Period"])


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_periods(
    session: AsyncSession = Depends(get_session), limit: int = 10, offset: int = 0
):
    return await PeriodService.get_periods(session=session, limit=limit, offset=offset)


@router.get("/{id}", response_model=PeriodRead, status_code=status.HTTP_200_OK)
async def get_period(id: UUID, session: AsyncSession = Depends(get_session)):
    return await PeriodService.get_period(id=id, session=session)
