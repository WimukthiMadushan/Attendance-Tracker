from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class PayrollPeriodBase(BaseModel):
    period_name: str
    start_date: date
    end_date: date
    status: str = "DRAFT"


class PayrollPeriodCreate(PayrollPeriodBase):
    pass


class PayrollRecordResponse(BaseModel):
    id: str
    payroll_period_id: str
    employee_id: str
    regular_hours: Decimal
    overtime_hours: Decimal
    hourly_rate: Decimal
    gross_pay: Decimal
    deductions: Decimal
    net_pay: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PayrollPeriodResponse(PayrollPeriodBase):
    id: str
    created_at: datetime
    updated_at: datetime
    records: List[PayrollRecordResponse] = []

    class Config:
        from_attributes = True
