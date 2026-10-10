from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.whatsapp import normalize_to_e164


class EmployeeBase(BaseModel):
    employee_code: str = Field(..., example="EMP-101")
    full_name: str = Field(..., example="Kasun Perera")
    phone_number: str = Field(..., example="+94771234567", description="Strict E.164 phone format")
    department_id: Optional[str] = Field(None, example="4eeece17-95f7-4455-a6bc-bc767e581d1d")
    employment_type: str = Field("FULL_TIME", example="FULL_TIME")
    monthly_base_salary: Decimal = Field(Decimal("185000.00"), example=185000.00)
    is_active: bool = True

    @field_validator("phone_number")
    def validate_phone(cls, v: str) -> str:
        return normalize_to_e164(v)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    employee_code: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    department_id: Optional[str] = None
    employment_type: Optional[str] = None
    monthly_base_salary: Optional[Decimal] = None
    is_active: Optional[bool] = None

    @field_validator("phone_number")
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return normalize_to_e164(v)
        return v


class EmployeeResponse(EmployeeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
