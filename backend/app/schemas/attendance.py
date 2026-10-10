from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class AttendanceLogBase(BaseModel):
    employee_id: str
    date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    total_hours: Optional[Decimal] = None
    status: str = "PRESENT"
    source: str = "WHATSAPP"
    notes: Optional[str] = None


class AttendanceLogCreate(AttendanceLogBase):
    pass


class AttendanceLogUpdate(BaseModel):
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    total_hours: Optional[Decimal] = None
    status: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class AttendanceLogResponse(AttendanceLogBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
