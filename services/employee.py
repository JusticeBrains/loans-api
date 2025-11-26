from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.company import Company
from models.employee import Employee
from models.user import User
from schemas.employee import EmployeeCreate, EmployeeUpdate
from schemas.base import ResponseModel


class EmployeeService:
    @staticmethod
    async def create_employee(
        data: EmployeeCreate, session: AsyncSession, current_user: User
    ):
        try:
            fullname = Employee.get_fullname(data)
            extra_fields = {"fullname": fullname, "user_id": current_user.id}
            if data.company_id:
                query = select(Company).where(Company.id == data.company_id)
                results = await session.exec(query)
                company = results.unique().one_or_none()
                if not company:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Company not found",
                    )
                extra_fields["company_name"] = company.name
            employee = Employee.model_validate(data, update=extra_fields)

            session.add(employee)
            await session.commit()
            await session.refresh(employee)

            return employee
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

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
    async def update_employee(
        id: UUID, data: EmployeeUpdate, session: AsyncSession, current_user: User
    ):
        employee = await EmployeeService.get_employee(id=id, session=session)
        employee_data = data.model_dump(exclude_unset=True)

        for key, value in employee_data.items():
            if value:
                setattr(employee, key, value)

        employee.modified_by_id = current_user.id
        session.add(employee)
        await session.commit()
        await session.refresh(employee)

        return employee

    @staticmethod
    async def get_employees(
        session: AsyncSession,
        company_id: UUID | None = None,
        code: str | None = None,
        firstname: str | None = None,
        lastname: str | None = None,
        middlename: str | None = None,
        company_name: str | None = None,
        fullname: str | None = None,
        national_id: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
        query = (
            select(Employee)
            .order_by(Employee.code)
            .limit(limit=limit)
            .offset(offset=offset)
        )

        if company_id:
            query = query.where(Employee.company_id == company_id)

        if code:
            query = query.where(Employee.code == code)

        if firstname:
            query = query.where(Employee.firstname == firstname)

        if lastname:
            query = query.where(Employee.lastname == lastname)

        if middlename:
            query = query.where(Employee.middlename == middlename)

        if company_name:
            query = query.where(Employee.company_name == company_name)

        if fullname:
            query = query.where(Employee.fullname == fullname)

        if national_id:
            query = query.where(Employee.national_id == national_id)

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
