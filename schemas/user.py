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
    admin_access: bool | None = False
    faab_admin: bool | None = False
    is_verified: str | None = None


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
    email: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    password: str | None = None
    company_id: uuid.UUID | None = None
    is_password_changed: bool | None = None
    is_password_reset: bool | None = None
    is_active: int | None = None


class UserLogin(SQLModel):
    username: str
    password: str


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshToken(SQLModel):
    refresh_token: str