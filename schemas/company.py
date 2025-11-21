import uuid
from datetime import datetime

from sqlmodel import SQLModel


class CompanyCreate(SQLModel):
    name: str


class CompanyRead(SQLModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime

class CompanyUpdate(SQLModel):
    name: str