from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class DailyTaskBase(BaseModel):
    employee_id: str
    attendance_log_id: Optional[str] = None
    date: date
    description: str
    duration_minutes: Optional[int] = None
    category: Optional[str] = "General"
    status: str = "COMPLETED"
    raw_message: Optional[str] = None
    ai_confidence: Optional[Decimal] = None


class DailyTaskCreate(DailyTaskBase):
    pass


class DailyTaskUpdate(BaseModel):
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    category: Optional[str] = None
    status: Optional[str] = None


class DailyTaskResponse(DailyTaskBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
