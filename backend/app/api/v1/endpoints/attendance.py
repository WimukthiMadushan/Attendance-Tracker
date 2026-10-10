from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Query
from app.schemas.attendance import AttendanceLogResponse

router = APIRouter()


@router.get("", response_model=List[AttendanceLogResponse])
async def list_attendance(
    employee_id: Optional[str] = Query(None),
    log_date: Optional[date] = Query(None, alias="date"),
):
    """Attendance summary endpoint."""
    return [
        {
            "id": "att-demo-1",
            "employee_id": employee_id or "emp-demo-1",
            "date": log_date or date.today(),
            "check_in_time": "2026-10-10T08:30:00Z",
            "check_out_time": "2026-10-10T17:00:00Z",
            "total_hours": 8.50,
            "status": "PRESENT",
            "source": "WHATSAPP",
            "notes": "Verified check-in via WhatsApp",
            "created_at": "2026-10-10T08:30:00Z",
            "updated_at": "2026-10-10T17:00:00Z",
        }
    ]
