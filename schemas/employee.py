from datetime import datetime
import uuid
from sqlmodel import SQLModel


class EmployeeBase(SQLModel):
    code: str
    firstname: str
    lastname: str
    middlename: str | None = None
    company_id: uuid.UUID
    user_id: uuid.UUID | None = None
    national_id: str | None = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class EmployeeUpdate(EmployeeBase):
    code: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    company_id: uuid.UUID | None = None
