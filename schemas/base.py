from typing import Generic, TypeVar, List
from datetime import datetime

from sqlmodel import SQLModel


class ResponseModel(SQLModel, Generic[TypeVar("T")]):
    count: int
    next: str | None = None
    previous: str | None = None
    results: List[T]
