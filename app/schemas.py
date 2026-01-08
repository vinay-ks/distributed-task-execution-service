from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class TaskCreate(BaseModel):
    name: str


class TaskResponse(BaseModel):
    id: UUID
    name: str
    status: str
    retry_count: int
    created_at: datetime

    class Config:
        orm_mode = True
