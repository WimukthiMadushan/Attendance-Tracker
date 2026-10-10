from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.core.database import db_client, get_prisma
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter()


@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    department_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List all employees in the employees table."""
    prisma = get_prisma()
    if prisma is not None and prisma.is_connected():
        where_filter = {}
        if department_id:
            where_filter["departmentId"] = department_id
        if is_active is not None:
            where_filter["isActive"] = is_active

        try:
            employees = await prisma.employee.find_many(
                where=where_filter,
                order={"createdAt": "desc"}
            )
            return [
                {
                    "id": e.id,
                    "employee_code": e.employeeCode,
                    "full_name": e.fullName,
                    "phone_number": e.phoneNumber,
                    "department_id": e.departmentId,
                    "employment_type": e.employmentType,
                    "monthly_base_salary": e.monthlyBaseSalary,
                    "is_active": e.isActive,
                    "created_at": e.createdAt,
                    "updated_at": e.updatedAt,
                }
                for e in employees
            ]
        except Exception:
            pass

    # Direct asyncpg pool query
    if db_client.is_connected:
        query = "SELECT * FROM employees WHERE 1=1"
        params = []
        if department_id:
            params.append(department_id)
            query += f" AND department_id = ${len(params)}"
        if is_active is not None:
            params.append(is_active)
            query += f" AND is_active = ${len(params)}"
        query += " ORDER BY created_at DESC"

        rows = await db_client.fetch(query, *params)
        return [
            {
                "id": r["id"],
                "employee_code": r["employee_code"],
                "full_name": r["full_name"],
                "phone_number": r["phone_number"],
                "department_id": r["department_id"],
                "employment_type": r["employment_type"],
                "monthly_base_salary": r["monthly_base_salary"],
                "is_active": r["is_active"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
            }
            for r in rows
        ]

    # Offline mock fallback
    return [
        {
            "id": "emp-demo-1",
            "employee_code": "EMP-101",
            "full_name": "Kasun Perera",
            "phone_number": "+94771234567",
            "department_id": None,
            "employment_type": "FULL_TIME",
            "monthly_base_salary": 185000.00,
            "is_active": True,
            "created_at": "2026-10-01T08:00:00Z",
            "updated_at": "2026-10-01T08:00:00Z",
        }
    ]


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate):
    """Create a new employee with strict phone number verification."""
    prisma = get_prisma()
    if prisma is not None and prisma.is_connected():
        existing = await prisma.employee.find_unique(where={"phoneNumber": payload.phone_number})
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Phone number {payload.phone_number} is already registered."
            )

        created = await prisma.employee.create(
            data={
                "employeeCode": payload.employee_code,
                "fullName": payload.full_name,
                "phoneNumber": payload.phone_number,
                "departmentId": payload.department_id,
                "employmentType": payload.employment_type,
                "monthlyBaseSalary": payload.monthly_base_salary,
                "isActive": payload.is_active,
            }
        )
        return {
            "id": created.id,
            "employee_code": created.employeeCode,
            "full_name": created.fullName,
            "phone_number": created.phoneNumber,
            "department_id": created.departmentId,
            "employment_type": created.employmentType,
            "monthly_base_salary": created.monthlyBaseSalary,
            "is_active": created.isActive,
            "created_at": created.createdAt,
            "updated_at": created.updatedAt,
        }

    if db_client.is_connected:
        existing = await db_client.fetchval(
            "SELECT id FROM employees WHERE phone_number = $1", payload.phone_number
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Phone number {payload.phone_number} is already registered."
            )

        row = await db_client.fetchrow(
            """
            INSERT INTO employees (
                employee_code, full_name, phone_number, department_id,
                employment_type, monthly_base_salary, is_active
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *;
            """,
            payload.employee_code,
            payload.full_name,
            payload.phone_number,
            payload.department_id,
            payload.employment_type,
            payload.monthly_base_salary,
            payload.is_active,
        )
        return {
            "id": row["id"],
            "employee_code": row["employee_code"],
            "full_name": row["full_name"],
            "phone_number": row["phone_number"],
            "department_id": row["department_id"],
            "employment_type": row["employment_type"],
            "monthly_base_salary": row["monthly_base_salary"],
            "is_active": row["is_active"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    raise HTTPException(status_code=503, detail="Database not connected")
