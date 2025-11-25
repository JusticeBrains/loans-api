import uuid
from datetime import datetime

from sqlmodel import SQLModel

from models import company


class UserBase(SQLModel):
    email: str
    firstname: str
    lastname: str
    middlename: str | None = None
    pin: str | None = None
    company_id: uuid.UUID | None = None
    is_super: int = 0


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: uuid.UUID
    username: str
    is_password_changed: bool
    is_password_reset: bool
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserUpdate(UserCreate):
    id: uuid.UUID
    email: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    password: str | None = None
    company_id: uuid.UUID | None = None
    is_password_changed: bool
    is_password_reset: bool
    is_active: int = 1


class UserLogin(SQLModel):
    username: str
    password: str


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
