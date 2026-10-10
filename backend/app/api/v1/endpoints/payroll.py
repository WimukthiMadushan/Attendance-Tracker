from typing import List
from fastapi import APIRouter
from app.schemas.payroll import PayrollPeriodResponse

router = APIRouter()


@router.get("/periods", response_model=List[PayrollPeriodResponse])
async def list_payroll_periods():
    """Payroll periods summary endpoint."""
    return [
        {
            "id": "period-demo-1",
            "period_name": "October 2026 - Bi-Weekly 1",
            "start_date": "2026-10-01",
            "end_date": "2026-10-15",
            "status": "DRAFT",
            "created_at": "2026-10-01T00:00:00Z",
            "updated_at": "2026-10-01T00:00:00Z",
            "records": [
                {
                    "id": "rec-demo-1",
                    "payroll_period_id": "period-demo-1",
                    "employee_id": "emp-demo-1",
                    "regular_hours": 40.00,
                    "overtime_hours": 2.50,
                    "hourly_rate": 25.00,
                    "gross_pay": 1062.50,
                    "deductions": 50.00,
                    "net_pay": 1012.50,
                    "status": "CALCULATED",
                    "created_at": "2026-10-10T00:00:00Z",
                    "updated_at": "2026-10-10T00:00:00Z",
                }
            ],
        }
    ]
