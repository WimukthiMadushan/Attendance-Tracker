import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional, Tuple, List

from app.core.database import get_db
from app.schemas.ai_parser import ParsedEmployeeMessage, IntentType, ExtractedTask

logger = logging.getLogger("attendance_tracker.attendance_service")


class AttendanceService:
    async def process_parsed_message(
        self,
        sender_phone: str,
        parsed: ParsedEmployeeMessage,
        raw_message_id: str,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Executes unified relational database operations based on LLM extracted intent.
        Returns: (success: bool, reply_message: str, employee_id: Optional[str])
        """
        db = get_db()
        today = date.today()
        now = datetime.now(timezone.utc)

        if db is None or not db.is_connected():
            logger.warning("Prisma client not connected. Operating in mock execution mode.")
            return True, parsed.reply_message, None

        # 1. Lookup Employee by strict E.164 WhatsApp number
        employee = await db.employee.find_unique(where={"whatsappPhone": sender_phone})
        if not employee:
            error_reply = (
                f"Hello! Your phone number ({sender_phone}) is not registered in the HR system. "
                f"Please contact HR to register your WhatsApp number."
            )
            return False, error_reply, None

        if not employee.isActive:
            return False, "Your employee account is currently marked as inactive. Please contact HR.", employee.id

        employee_id = employee.id

        # 2. Process according to intent
        if parsed.intent == IntentType.CHECK_IN:
            await self._handle_check_in(db, employee_id, today, now)
        elif parsed.intent == IntentType.CHECK_OUT:
            await self._handle_check_out(db, employee_id, today, now)
        elif parsed.intent == IntentType.CHECK_OUT_WITH_TASKS:
            log = await self._handle_check_out(db, employee_id, today, now)
            if parsed.tasks:
                await self._save_tasks(db, employee_id, log.id, today, parsed.tasks, raw_message_id, parsed.confidence_score)
        elif parsed.intent == IntentType.TASK_LOG:
            log = await self._ensure_daily_log(db, employee_id, today)
            if parsed.tasks:
                await self._save_tasks(db, employee_id, log.id, today, parsed.tasks, raw_message_id, parsed.confidence_score)
        elif parsed.intent == IntentType.LEAVE_REQUEST:
            await self._handle_leave(db, employee_id, today, parsed.notes)

        return True, parsed.reply_message, employee_id

    async def _ensure_daily_log(self, db, employee_id: str, log_date: date):
        """
        Finds or creates unified attendance record respecting composite unique constraint [employeeId, date].
        """
        log = await db.attendancelog.find_unique(
            where={"employee_date_unique": {"employeeId": employee_id, "date": log_date}}
        )
        if not log:
            log = await db.attendancelog.create(
                data={
                    "employeeId": employee_id,
                    "date": log_date,
                    "status": "PRESENT",
                    "source": "WHATSAPP",
                }
            )
        return log

    async def _handle_check_in(self, db, employee_id: str, log_date: date, check_in_dt: datetime):
        log = await db.attendancelog.find_unique(
            where={"employee_date_unique": {"employeeId": employee_id, "date": log_date}}
        )
        if not log:
            log = await db.attendancelog.create(
                data={
                    "employeeId": employee_id,
                    "date": log_date,
                    "checkInTime": check_in_dt,
                    "status": "PRESENT",
                    "source": "WHATSAPP",
                }
            )
        elif not log.checkInTime:
            log = await db.attendancelog.update(
                where={"id": log.id},
                data={"checkInTime": check_in_dt}
            )
        return log

    async def _handle_check_out(self, db, employee_id: str, log_date: date, check_out_dt: datetime):
        log = await self._ensure_daily_log(db, employee_id, log_date)

        total_hours = None
        if log.checkInTime:
            # Calculate duration in hours
            diff = (check_out_dt - log.checkInTime).total_seconds() / 3600.0
            total_hours = Decimal(str(round(max(diff, 0.0), 2)))

        update_data = {"checkOutTime": check_out_dt}
        if total_hours is not None:
            update_data["totalHours"] = total_hours

        log = await db.attendancelog.update(
            where={"id": log.id},
            data=update_data
        )
        return log

    async def _handle_leave(self, db, employee_id: str, log_date: date, notes: Optional[str]):
        log = await db.attendancelog.find_unique(
            where={"employee_date_unique": {"employeeId": employee_id, "date": log_date}}
        )
        if not log:
            await db.attendancelog.create(
                data={
                    "employeeId": employee_id,
                    "date": log_date,
                    "status": "ON_LEAVE",
                    "source": "WHATSAPP",
                    "notes": notes or "Leave requested via WhatsApp",
                }
            )
        else:
            await db.attendancelog.update(
                where={"id": log.id},
                data={
                    "status": "ON_LEAVE",
                    "notes": notes or log.notes,
                }
            )

    async def _save_tasks(
        self,
        db,
        employee_id: str,
        attendance_log_id: str,
        task_date: date,
        tasks: List[ExtractedTask],
        raw_message_id: str,
        confidence_score: float
    ):
        for t in tasks:
            await db.dailytask.create(
                data={
                    "employeeId": employee_id,
                    "attendanceLogId": attendance_log_id,
                    "date": task_date,
                    "description": t.description,
                    "durationMinutes": t.duration_minutes,
                    "category": t.category,
                    "status": t.status,
                    "rawMessage": f"Source: {raw_message_id}",
                    "aiConfidence": Decimal(str(round(confidence_score, 2))),
                }
            )


attendance_service = AttendanceService()
