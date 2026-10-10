from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskItemBase(BaseModel):
    employee_id: str = Field(..., example="edab5855-9d1a-4663-978c-5561bae8180f")
    task_description: str = Field(..., example="Implemented async connection pool for PostgreSQL")


class TaskItemCreate(TaskItemBase):
    pass


class TaskItemUpdate(BaseModel):
    task_description: Optional[str] = None


class TaskItemResponse(TaskItemBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
