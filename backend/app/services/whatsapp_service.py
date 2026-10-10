import logging
from typing import Dict, Any, Optional, Set
import httpx

from app.core.config import settings
from app.schemas.whatsapp import InboundMessageDetail
from app.services.llm_parser_service import llm_parser_service
from app.services.attendance_service import attendance_service

logger = logging.getLogger("attendance_tracker.whatsapp_service")


class WhatsAppService:
    def __init__(self):
        # In-memory deduplication cache for message idempotency
        self._seen_message_ids: Set[str] = set()

    async def process_inbound_message(self, message: InboundMessageDetail) -> Dict[str, Any]:
        """Process incoming WhatsApp message with deduplication, AI parsing, and reply dispatch."""
        message_id = message.message_id
        sender_phone = message.sender_phone

        # 1. Idempotency guard
        if message_id in self._seen_message_ids:
            logger.info(f"Duplicate message ignored: {message_id}")
            return {"status": "duplicate_ignored", "message_id": message_id}
        self._seen_message_ids.add(message_id)

        # 2. Parse message with LLM / Heuristic parser
        try:
            parsed = await llm_parser_service.parse_message(
                message_text=message.text_body, sender_phone=sender_phone
            )
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            reply = "Thank you for your message. We received your request."
            await self.send_text_message(sender_phone, reply)
            return {"status": "error", "message_id": message_id}

        # 3. Persist tasks if present
        success, reply_text, employee_id = await attendance_service.process_parsed_message(
            sender_phone=sender_phone,
            parsed=parsed,
            raw_message_id=message_id,
        )

        # 4. Dispatch WhatsApp reply
        await self.send_text_message(sender_phone, reply_text)

        return {
            "status": "processed" if success else "failed",
            "message_id": message_id,
            "employee_id": employee_id,
            "reply_sent": reply_text,
        }

    async def send_text_message(self, to_phone: str, message_text: str) -> bool:
        """Sends an outbound WhatsApp text message via Meta Cloud API."""
        clean_phone = to_phone.replace("+", "")
        token = settings.META_ACCESS_TOKEN

        # Avoid real API call if running with placeholder credentials
        if not token or "placeholder" in token.lower() or token.startswith("EAAxxx"):
            logger.info(f"[SIMULATED WHATSAPP OUTBOUND] To: {to_phone} | Message: {message_text}")
            return True

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {"preview_url": False, "body": message_text},
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    settings.meta_graph_url,
                    json=payload,
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                )
                return resp.status_code == 200
        except Exception as e:
            logger.error(f"Failed to dispatch WhatsApp message to {to_phone}: {e}")
            return False


whatsapp_service = WhatsAppService()
