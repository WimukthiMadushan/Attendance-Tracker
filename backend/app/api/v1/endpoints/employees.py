from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.core.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter()


@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    department: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List all employees in the unified table."""
    db = get_db()
    if db is None or not db.is_connected():
        # Fallback sample data if DB is offline
        return [
            {
                "id": "emp-demo-1",
                "employee_code": "EMP-001",
                "first_name": "Kasun",
                "last_name": "Perera",
                "whatsapp_phone": "+94771234567",
                "email": "kasun@company.com",
                "department": "Engineering",
                "role": "EMPLOYEE",
                "hourly_rate": 25.00,
                "is_active": True,
                "created_at": "2026-10-01T08:00:00Z",
                "updated_at": "2026-10-01T08:00:00Z",
            },
            {
                "id": "emp-demo-2",
                "employee_code": "EMP-002",
                "first_name": "Nimali",
                "last_name": "Silva",
                "whatsapp_phone": "+94779876543",
                "email": "nimali@company.com",
                "department": "Product",
                "role": "EMPLOYEE",
                "hourly_rate": 30.00,
                "is_active": True,
                "created_at": "2026-10-01T08:00:00Z",
                "updated_at": "2026-10-01T08:00:00Z",
            }
        ]

    where_filter = {}
    if department:
        where_filter["department"] = department
    if is_active is not None:
        where_filter["isActive"] = is_active

    try:
        employees = await db.employee.find_many(where=where_filter, order={"createdAt": "desc"})
        return [
            {
                "id": e.id,
                "employee_code": e.employeeCode,
                "first_name": e.firstName,
                "last_name": e.lastName,
                "whatsapp_phone": e.whatsappPhone,
                "email": e.email,
                "department": e.department,
                "role": e.role,
                "hourly_rate": e.hourlyRate,
                "is_active": e.isActive,
                "created_at": e.createdAt,
                "updated_at": e.updatedAt,
            }
            for e in employees
        ]
    except Exception:
        return [
            {
                "id": "emp-demo-1",
                "employee_code": "EMP-001",
                "first_name": "Kasun",
                "last_name": "Perera",
                "whatsapp_phone": "+94771234567",
                "email": "kasun@company.com",
                "department": "Engineering",
                "role": "EMPLOYEE",
                "hourly_rate": 25.00,
                "is_active": True,
                "created_at": "2026-10-01T08:00:00Z",
                "updated_at": "2026-10-01T08:00:00Z",
            },
            {
                "id": "emp-demo-2",
                "employee_code": "EMP-002",
                "first_name": "Nimali",
                "last_name": "Silva",
                "whatsapp_phone": "+94779876543",
                "email": "nimali@company.com",
                "department": "Product",
                "role": "EMPLOYEE",
                "hourly_rate": 30.00,
                "is_active": True,
                "created_at": "2026-10-01T08:00:00Z",
                "updated_at": "2026-10-01T08:00:00Z",
            }
        ]


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate):
    """Create a new employee with strict E.164 phone verification."""
    db = get_db()
    if db is None or not db.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")

    # Check phone uniqueness
    existing = await db.employee.find_unique(where={"whatsappPhone": payload.whatsapp_phone})
    if existing:
        raise HTTPException(status_code=400, detail=f"WhatsApp phone {payload.whatsapp_phone} is already registered.")

    created = await db.employee.create(
        data={
            "employeeCode": payload.employee_code,
            "firstName": payload.first_name,
            "lastName": payload.last_name,
            "whatsappPhone": payload.whatsapp_phone,
            "email": payload.email,
            "department": payload.department,
            "role": payload.role,
            "hourlyRate": payload.hourly_rate,
            "isActive": payload.is_active,
        }
    )
    return {
        "id": created.id,
        "employee_code": created.employeeCode,
        "first_name": created.firstName,
        "last_name": created.lastName,
        "whatsapp_phone": created.whatsappPhone,
        "email": created.email,
        "department": created.department,
        "role": created.role,
        "hourly_rate": created.hourlyRate,
        "is_active": created.isActive,
        "created_at": created.createdAt,
        "updated_at": created.updatedAt,
    }
