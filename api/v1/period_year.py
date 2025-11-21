from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from config.db import get_session
from schemas.base import ResponseModel
from schemas.period_year import PeriodYearCreate, PeriodYearRead
from services.period_year import PeriodYearService


router = APIRouter(prefix="/period_year", tags=["Period Year"])


@router.get("/{id}", response_model=PeriodYearRead, status_code=status.HTTP_200_OK)
async def get_period_year(id: UUID, session: AsyncSession = Depends(get_session)):
    return await PeriodYearService.get_period(id=id, session=session)


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_period_years(session: AsyncSession = Depends(get_session)):
    return await PeriodYearService.get_periods(session=session)


@router.delete("/{id}", response_model={}, status_code=status.HTTP_204_NO_CONTENT)
async def delete_period_year(id: UUID, session: AsyncSession = Depends(get_session)):
    return await PeriodYearService.delete_period(id=id, session=session)


@router.post("/", response_model=PeriodYearRead, status_code=status.HTTP_201_CREATED)
async def create_period_year(
    data: PeriodYearCreate, session: AsyncSession = Depends(get_session)
):
    return await PeriodYearService.create_period_year(data=data, session=session)

