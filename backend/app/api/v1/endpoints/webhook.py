import logging
from typing import Any, Dict
from fastapi import APIRouter, Query, Response, status, Request
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.schemas.whatsapp import InboundMessageDetail, normalize_to_e164
from app.services.whatsapp_service import whatsapp_service

logger = logging.getLogger("task_tracker.webhook")

router = APIRouter()


@router.get("", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Meta WhatsApp Cloud API Webhook Verification Endpoint.
    Meta sends a GET request to verify the webhook URL with hub.mode, hub.challenge, and hub.verify_token.
    """
    logger.info(f"Webhook verification request: mode={hub_mode}, verify_token={hub_verify_token}")

    if hub_mode == "subscribe" and hub_verify_token == settings.META_VERIFY_TOKEN:
        logger.info("Webhook verification successful.")
        return Response(content=hub_challenge, media_type="text/plain", status_code=status.HTTP_200_OK)

    logger.warning("Webhook verification failed: token mismatch or invalid mode.")
    return Response(content="Verification token mismatch", media_type="text/plain", status_code=status.HTTP_403_FORBIDDEN)


@router.post("")
async def receive_webhook(request: Request) -> Dict[str, Any]:
    """
    Meta WhatsApp Cloud API Inbound Webhook Receiver.
    Extracts incoming messages and performs idempotent processing using message_id.
    Always returns HTTP 200 OK to acknowledge receipt to Meta.
    """
    payload = await request.json()
    logger.info("Received WhatsApp webhook event.")

    # Validate top level payload structure
    entry_list = payload.get("entry", [])
    if not entry_list:
        return {"status": "no_entries"}

    results = []

    for entry in entry_list:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])

            for msg in messages:
                message_id = msg.get("id")
                from_raw = msg.get("from")
                msg_type = msg.get("type", "unknown")
                timestamp = msg.get("timestamp", "")

                if not message_id or not from_raw:
                    continue

                # Normalize phone to strict E.164
                sender_e164 = normalize_to_e164(from_raw)

                # Extract text body if available
                text_body = ""
                if msg_type == "text":
                    text_body = msg.get("text", {}).get("body", "")
                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    button_reply = interactive.get("button_reply", {})
                    list_reply = interactive.get("list_reply", {})
                    text_body = button_reply.get("title") or list_reply.get("title") or ""

                if not text_body:
                    logger.info(f"Skipping unsupported message type {msg_type} (id: {message_id})")
                    continue

                inbound_detail = InboundMessageDetail(
                    message_id=message_id,
                    sender_phone=sender_e164,
                    text_body=text_body,
                    timestamp=timestamp,
                    message_type=msg_type,
                    raw_payload=msg,
                )

                # Execute idempotent processing
                result = await whatsapp_service.process_inbound_message(inbound_detail)
                results.append(result)

    return {"status": "acknowledged", "processed_count": len(results), "details": results}
