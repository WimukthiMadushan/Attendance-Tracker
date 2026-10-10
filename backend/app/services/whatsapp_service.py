import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Set
import httpx

from app.core.config import settings
from app.core.database import get_db
from app.schemas.whatsapp import InboundMessageDetail, normalize_to_e164
from app.services.llm_parser_service import llm_parser_service
from app.services.attendance_service import attendance_service

logger = logging.getLogger("attendance_tracker.whatsapp_service")


class WhatsAppService:
    def __init__(self):
        # Fallback cache for idempotency tracking when database connection is offline
        self._seen_message_ids: Set[str] = set()

    async def process_inbound_message(self, message: InboundMessageDetail) -> Dict[str, Any]:
        """
        Processes an incoming WhatsApp message with strict idempotency using message_id.
        """
        db = get_db()
        message_id = message.message_id
        sender_phone = message.sender_phone

        logger.info(f"Incoming message ID: {message_id} from {sender_phone}")

        # ----------------------------------------------------------------------
        # 1. IDEMPOTENCY CHECK
        # ----------------------------------------------------------------------
        # Check in-memory deduplication cache first
        if message_id in self._seen_message_ids:
            logger.warning(f"Duplicate message ignored via memory guard: {message_id}")
            return {
                "status": "duplicate_ignored",
                "message_id": message_id,
                "reason": "already_processed",
            }

        # Check database deduplication if online
        if db is not None:
            try:
                existing = await db.processedwebhookmessage.find_unique(
                    where={"messageId": message_id}
                )
                if existing:
                    self._seen_message_ids.add(message_id)
                    logger.warning(f"Duplicate message ignored via database: {message_id} (Status: {existing.status})")
                    return {
                        "status": "duplicate_ignored",
                        "message_id": message_id,
                        "previous_status": existing.status,
                    }

                # Create preliminary audit log with status RECEIVED
                await db.processedwebhookmessage.create(
                    data={
                        "messageId": message_id,
                        "senderPhone": sender_phone,
                        "messageType": message.message_type,
                        "rawPayload": json.dumps(message.raw_payload),
                        "status": "RECEIVED",
                    }
                )
            except Exception as e:
                logger.warning(f"Database idempotency audit skipped ({e}). Using memory guard.")

        # Register message_id to prevent duplicates
        self._seen_message_ids.add(message_id)

        # ----------------------------------------------------------------------
        # 2. AI PARSER (LLM structured extraction)
        # ----------------------------------------------------------------------
        reply_text = "Message received."
        employee_id = None
        status = "PROCESSED"
        err_msg = None

        try:
            parsed = await llm_parser_service.parse_message(
                message_text=message.text_body,
                sender_phone=sender_phone
            )
            logger.info(f"Parsed intent: {parsed.intent} (Confidence: {parsed.confidence_score})")

            # ------------------------------------------------------------------
            # 3. ATTENDANCE & TASK PERSISTENCE
            # ------------------------------------------------------------------
            try:
                success, reply_text, employee_id = await attendance_service.process_parsed_message(
                    sender_phone=sender_phone,
                    parsed=parsed,
                    raw_message_id=message_id,
                )
                if not success:
                    status = "FAILED"
                    err_msg = reply_text
            except Exception as e:
                logger.warning(f"Attendance persistence fallback ({e}).")
                reply_text = parsed.reply_message

        except Exception as e:
            logger.error(f"Error parsing message {message_id}: {e}", exc_info=True)
            status = "FAILED"
            err_msg = str(e)
            reply_text = "We encountered an issue processing your request. Please try again shortly."

        # ----------------------------------------------------------------------
        # 4. UPDATE AUDIT & IDEMPOTENCY RECORD
        # ----------------------------------------------------------------------
        if db is not None:
            try:
                update_data = {
                    "status": status,
                    "errorMessage": err_msg,
                    "processedAt": datetime.now(timezone.utc),
                }
                if employee_id:
                    update_data["employeeId"] = employee_id

                await db.processedwebhookmessage.update(
                    where={"messageId": message_id},
                    data=update_data,
                )
            except Exception as e:
                logger.debug(f"Audit log update skipped ({e}).")

        # ----------------------------------------------------------------------
        # 5. DISPATCH OUTBOUND WHATSAPP REPLY
        # ----------------------------------------------------------------------
        await self.send_text_message(to_phone=sender_phone, message_text=reply_text)

        return {
            "status": status,
            "message_id": message_id,
            "reply_sent": reply_text,
            "employee_id": employee_id,
        }

    async def send_text_message(self, to_phone: str, message_text: str) -> bool:
        """
        Sends an outbound WhatsApp text message via Meta Cloud API.
        """
        clean_phone = to_phone.replace("+", "")
        token = settings.META_ACCESS_TOKEN

        # Check for placeholder credentials
        if not token or "placeholder" in token.lower() or "xxxx" in token.lower():
            logger.info(f"[Mock Outbound WhatsApp] To: {to_phone} | Text: '{message_text}'")
            return True

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {"preview_url": False, "body": message_text},
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(settings.meta_graph_url, headers=headers, json=payload)
                if res.status_code >= 400:
                    logger.error(f"Meta WhatsApp API error: {res.status_code} {res.text}")
                    return False
                return True
        except Exception as e:
            logger.error(f"Failed to send outbound WhatsApp message to {to_phone}: {e}")
            return False


whatsapp_service = WhatsAppService()
