from uuid import UUID

from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.company import CompanyRead, CompanyCreate, CompanyUpdate
from schemas.base import ResponseModel

from config.db import get_session
from services.company import CompanyService


router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate, session: AsyncSession = Depends(get_session)
):
    return await CompanyService.create_company(data=data, session=session)


@router.get("/{id}", response_model=CompanyRead, status_code=status.HTTP_200_OK)
async def get_company(id: UUID, session: AsyncSession = Depends(get_session)):
    return await CompanyService.get_company(id=id, session=session)


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_companies(
    session: AsyncSession = Depends(get_session), limit: int = 10, offset: int = 0
):
    return await CompanyService.get_companies(
        session=session, limit=limit, offset=offset
    )


@router.patch("/{id}", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def update_company(
    id: UUID, data: CompanyUpdate, session: AsyncSession = Depends(get_session)
):
    return await CompanyService.update_company(id=id, data=data, session=session)


@router.delete("/{id}", response_model={}, status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(id: UUID, session: AsyncSession = Depends(get_session)):
    return await CompanyService.delete_company(id=id, session=session)
