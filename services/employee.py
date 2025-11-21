from unittest import result
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from config.db import get_session
from models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeUpdate
from schemas.base import ResponseModel


class EmployeeService:

    @staticmethod
    async def create_employee(data: EmployeeCreate, session: AsyncSession):
        fullname = Employee.get_fullname(data)
        extra_fields = {"fullname": fullname}
        employee = Employee.model_validate(data, update=extra_fields)

        session.add(employee)
        await session.commit()
        await session.refresh(employee)

        return employee

    @staticmethod
    async def get_employee(id: UUID, session: AsyncSession):
        query = select(Employee).where(Employee.id == id)
        results = await session.exec(query)
        employee = results.unique().one_or_none()

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
            )

        return employee

    @staticmethod
    async def update_employee(id: UUID, data: EmployeeUpdate, session: AsyncSession):
        employee = await EmployeeService.get_employee(id=id, session=session)
        employee_data = data.model_dump(exclude_unset=True)

        for key, value in employee_data.items():
            if value:
                setattr(employee, key, value)

        session.add(employee)
        await session.commit()
        await session.refresh(employee)

        return employee

    @staticmethod
    async def get_employees(session: AsyncSession, limit: int = 10, offset: int = 0):
        query = (
            select(Employee)
            .order_by(Employee.code)
            .limit(limit=limit)
            .offset(offset=offset)
        )

        results = await session.exec(query)
        all_employees = results.unique().all()
        count = len(all_employees)

        return ResponseModel(count=count, results=all_employees)

    @staticmethod
    async def delete_employee(id: UUID, session: AsyncSession):
        employee = await EmployeeService.get_employee(id=id, session=session)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
            )

        await session.delete(employee)
        await session.commit()

        return {}
