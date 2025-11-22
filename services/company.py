from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from models.company import Company
from schemas.company import CompanyCreate, CompanyUpdate
from schemas.base import ResponseModel


class CompanyService:

    @staticmethod
    async def create_company(data: CompanyCreate, session: AsyncSession):
        company = Company(**data.model_dump())
        
        session.add(company)
        await session.commit()
        await session.refresh(company)

        return company

    @staticmethod
    async def get_companies(session: AsyncSession, limit: int = 10, offset: int = 0):
        query = (
            select(Company)
            .order_by(Company.created_at.desc())
            .limit(limit=limit)
            .offset(offset=offset)
        )

        results = await session.exec(query)
        companies = results.unique().all()

        count = len(companies)

        return ResponseModel(
            count=count,
            results=companies,
        )

    @staticmethod
    async def get_company(id: UUID, session: AsyncSession):
        query = select(Company).where(Company.id == id)
        result = await session.exec(query)

        company = result.unique().one_or_none()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
            )

        return company

    @staticmethod
    async def update_company(id: UUID, data: CompanyUpdate, session: AsyncSession):
        company = await CompanyService.get_company(id=id, session=session)

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
            )

        for key, value in data.model_dump().items():
            if value:
                setattr(company, key, value)

        session.add(company)
        await session.commit()
        await session.refresh(company)

        return company

    @staticmethod
    async def delete_company(id: UUID, session: AsyncSession):
        company = await CompanyService.get_company(id=id, session=session)

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
            )
        await session.delete(company)
        await session.commit()

        return {}
