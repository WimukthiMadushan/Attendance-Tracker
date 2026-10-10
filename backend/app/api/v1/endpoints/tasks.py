from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.core.database import db_client, get_prisma
from app.schemas.task_item import TaskItemCreate, TaskItemResponse

router = APIRouter()


@router.get("", response_model=List[TaskItemResponse])
async def list_task_items(
    employee_id: Optional[str] = Query(None),
):
    """Query task items across all employees."""
    prisma = get_prisma()
    if prisma is not None and prisma.is_connected():
        where_filter = {}
        if employee_id:
            where_filter["employeeId"] = employee_id

        try:
            tasks = await prisma.taskitem.find_many(
                where=where_filter,
                order={"createdAt": "desc"}
            )
            return [
                {
                    "id": t.id,
                    "employee_id": t.employeeId,
                    "task_description": t.taskDescription,
                    "created_at": t.createdAt,
                }
                for t in tasks
            ]
        except Exception:
            pass

    if db_client.is_connected:
        query = "SELECT * FROM task_items WHERE 1=1"
        params = []
        if employee_id:
            params.append(employee_id)
            query += f" AND employee_id = ${len(params)}"
        query += " ORDER BY created_at DESC"

        rows = await db_client.fetch(query, *params)
        return [
            {
                "id": r["id"],
                "employee_id": r["employee_id"],
                "task_description": r["task_description"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    # Offline mock fallback
    return [
        {
            "id": "task-demo-1",
            "employee_id": "emp-demo-1",
            "task_description": "Configured database layer and connection pooling",
            "created_at": "2026-10-10T11:00:00Z",
        }
    ]


@router.post("", response_model=TaskItemResponse, status_code=status.HTTP_201_CREATED)
async def create_task_item(payload: TaskItemCreate):
    """Create a new task item for an employee."""
    prisma = get_prisma()
    if prisma is not None and prisma.is_connected():
        created = await prisma.taskitem.create(
            data={
                "employeeId": payload.employee_id,
                "taskDescription": payload.task_description,
            }
        )
        return {
            "id": created.id,
            "employee_id": created.employeeId,
            "task_description": created.taskDescription,
            "created_at": created.createdAt,
        }

    if db_client.is_connected:
        row = await db_client.fetchrow(
            """
            INSERT INTO task_items (employee_id, task_description)
            VALUES ($1, $2)
            RETURNING *;
            """,
            payload.employee_id,
            payload.task_description,
        )
        return {
            "id": row["id"],
            "employee_id": row["employee_id"],
            "task_description": row["task_description"],
            "created_at": row["created_at"],
        }

    raise HTTPException(status_code=503, detail="Database not connected")
