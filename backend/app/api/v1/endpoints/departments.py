from typing import List
from fastapi import APIRouter, HTTPException, status

from app.core.database import db_client, get_prisma
from app.schemas.department import DepartmentCreate, DepartmentResponse

router = APIRouter()


@router.get("", response_model=List[DepartmentResponse])
async def list_departments():
    """List all departments."""
    prisma = get_prisma()
    if prisma is not None and prisma.is_connected():
        try:
            departments = await prisma.department.find_many(order={"name": "asc"})
            return [
                {
                    "id": d.id,
                    "name": d.name,
                    "created_at": d.createdAt,
                }
                for d in departments
            ]
        except Exception:
            pass

    if db_client.is_connected:
        rows = await db_client.fetch("SELECT * FROM departments ORDER BY name ASC")
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    return [
        {"id": "dept-1", "name": "Engineering", "created_at": "2026-10-01T08:00:00Z"},
        {"id": "dept-2", "name": "Operations", "created_at": "2026-10-01T08:00:00Z"},
    ]


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(payload: DepartmentCreate):
    """Create a new department."""
    prisma = get_prisma()
    if prisma is not None and prisma.is_connected():
        created = await prisma.department.create(data={"name": payload.name})
        return {
            "id": created.id,
            "name": created.name,
            "created_at": created.createdAt,
        }

    if db_client.is_connected:
        row = await db_client.fetchrow(
            "INSERT INTO departments (name) VALUES ($1) RETURNING *;",
            payload.name,
        )
        return {
            "id": row["id"],
            "name": row["name"],
            "created_at": row["created_at"],
        }

    raise HTTPException(status_code=503, detail="Database not connected")
