import uuid
from datetime import datetime

from sqlmodel import SQLModel

from models import company


class UserCreate(SQLModel):
    email: str
    firstname: str
    lastname: str
    middlename: str | None = None
    password: str
    pin: str | None = None
    company_id: uuid.UUID
    is_super: bool = False


class UserRead(UserCreate):
    id: uuid.UUID
    is_password_changed: bool
    is_password_reset: bool
    is_active: bool
    company: company.Company
    created_at: datetime
    updated_at: datetime


class UserUpdate(UserCreate):
    id: uuid.UUID
    email: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    password: str | None = None
    company_id: uuid.UUID | None = None
    is_password_changed: bool
    is_password_reset: bool
    is_active: bool
