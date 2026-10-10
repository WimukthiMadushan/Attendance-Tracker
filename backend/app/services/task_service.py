import logging
from typing import Optional, Tuple
from app.core.database import db_client, get_prisma
from app.schemas.ai_parser import ParsedEmployeeMessage

logger = logging.getLogger("attendance_tracker.task_service")


class TaskService:
    async def process_parsed_message(
        self,
        sender_phone: str,
        parsed: ParsedEmployeeMessage,
        raw_message_id: str,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Process incoming employee task message and persist task items to database.
        Returns: (success: bool, reply_message: str, employee_id: Optional[str])
        """
        prisma = get_prisma()
        employee_id: Optional[str] = None

        # 1. Lookup Employee by registered phone number
        if prisma is not None and prisma.is_connected():
            employee = await prisma.employee.find_unique(where={"phoneNumber": sender_phone})
            if employee:
                employee_id = employee.id
                if not employee.isActive:
                    return False, "Your account is marked inactive. Please contact HR.", employee.id
        elif db_client.is_connected:
            row = await db_client.fetchrow(
                "SELECT id, is_active FROM employees WHERE phone_number = $1", sender_phone
            )
            if row:
                employee_id = row["id"]
                if not row["is_active"]:
                    return False, "Your account is marked inactive. Please contact HR.", employee_id

        if not employee_id:
            return False, f"Phone number {sender_phone} is not registered in the system.", None

        # 2. Persist extracted tasks to task_items table
        if parsed.tasks:
            for task in parsed.tasks:
                if prisma is not None and prisma.is_connected():
                    await prisma.taskitem.create(
                        data={
                            "employeeId": employee_id,
                            "taskDescription": task.description,
                        }
                    )
                elif db_client.is_connected:
                    await db_client.execute(
                        "INSERT INTO task_items (employee_id, task_description) VALUES ($1, $2)",
                        employee_id,
                        task.description,
                    )

        return True, parsed.reply_message, employee_id


task_service = TaskService()
