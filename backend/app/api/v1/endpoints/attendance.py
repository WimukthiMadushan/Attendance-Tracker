from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Query

from app.core.database import get_db
from app.schemas.attendance import AttendanceLogResponse

router = APIRouter()


@router.get("", response_model=List[AttendanceLogResponse])
async def list_attendance(
    employee_id: Optional[str] = Query(None),
    log_date: Optional[date] = Query(None, alias="date"),
):
    """Query unified attendance records."""
    db = get_db()
    if db is None or not db.is_connected():
        return [
            {
                "id": "att-demo-1",
                "employee_id": "emp-demo-1",
                "date": "2026-10-10",
                "check_in_time": "2026-10-10T08:30:00Z",
                "check_out_time": "2026-10-10T17:00:00Z",
                "total_hours": 8.50,
                "status": "PRESENT",
                "source": "WHATSAPP",
                "notes": "Logged via WhatsApp",
                "created_at": "2026-10-10T08:30:00Z",
                "updated_at": "2026-10-10T17:00:00Z",
            }
        ]

    where_filter = {}
    if employee_id:
        where_filter["employeeId"] = employee_id
    if log_date:
        where_filter["date"] = log_date

    try:
        records = await db.attendancelog.find_many(where=where_filter, order={"date": "desc"})
        return [
            {
                "id": r.id,
                "employee_id": r.employeeId,
                "date": r.date,
                "check_in_time": r.checkInTime,
                "check_out_time": r.checkOutTime,
                "total_hours": r.totalHours,
                "status": r.status,
                "source": r.source,
                "notes": r.notes,
                "created_at": r.createdAt,
                "updated_at": r.updatedAt,
            }
            for r in records
        ]
    except Exception:
        return [
            {
                "id": "att-demo-1",
                "employee_id": "emp-demo-1",
                "date": "2026-10-10",
                "check_in_time": "2026-10-10T08:30:00Z",
                "check_out_time": "2026-10-10T17:00:00Z",
                "total_hours": 8.50,
                "status": "PRESENT",
                "source": "WHATSAPP",
                "notes": "Logged via WhatsApp",
                "created_at": "2026-10-10T08:30:00Z",
                "updated_at": "2026-10-10T17:00:00Z",
            }
        ]
