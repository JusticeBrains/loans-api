import re
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.status import HTTP_200_OK

from config.db import get_session
from schemas.base import ResponseModel
from schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from services.employee import EmployeeService


router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate, session: AsyncSession = Depends(get_session)
):
    return await EmployeeService.create_employee(data=data, session=session)


@router.get("/{id}", response_model=EmployeeRead, status_code=HTTP_200_OK)
async def get_employee(id: UUID, session: AsyncSession = Depends(get_session)):
    return await EmployeeService.get_employee(id=id, session=session)


@router.get("/", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def get_employees(
    session: AsyncSession = Depends(get_session), limit: int = 10, offset: int = 0
):
    return await EmployeeService.get_employees(
        session=session, limit=limit, offset=offset
    )


@router.patch("/{id}", response_model=EmployeeRead, status_code=status.HTTP_200_OK)
async def update_employee(
    id: UUID, data: EmployeeUpdate, session: AsyncSession = Depends(get_session)
):
    return await EmployeeService.update_employee(id=id, data=data, session=session)


@router.delete("/{id}", response_model={}, status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(id: UUID, session: AsyncSession = Depends(get_session)):
    return await EmployeeService.delete_employee(id=id, session=session)
