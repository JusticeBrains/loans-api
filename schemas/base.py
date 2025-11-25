import uuid
from datetime import datetime

from sqlmodel import SQLModel


class ResponseModel(SQLModel):
    count: int
    next: str | None = None
    previous: str | None = None
    results: list
