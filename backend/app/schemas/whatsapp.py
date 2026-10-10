import re
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator

# E.164 regular expression: starts with '+', followed by 1 to 15 digits (first digit 1-9)
E164_REGEX = r"^\+[1-9]\d{1,14}$"


def normalize_to_e164(phone: str) -> str:
    """
    Normalizes a phone number to strict E.164 format.
    Ensures '+' prefix and removes spaces, dashes, or parentheses.
    """
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    if not cleaned.startswith("+"):
        cleaned = f"+{cleaned}"
    if not re.match(E164_REGEX, cleaned):
        raise ValueError(f"Phone number '{phone}' does not conform to E.164 format (+[1-9]\\d{{1,14}})")
    return cleaned


class WhatsAppWebhookVerification(BaseModel):
    hub_mode: Optional[str] = Field(None, alias="hub.mode")
    hub_challenge: Optional[str] = Field(None, alias="hub.challenge")
    hub_verify_token: Optional[str] = Field(None, alias="hub.verify_token")


class WhatsAppTextMessage(BaseModel):
    body: str


class WhatsAppMessageItem(BaseModel):
    id: str = Field(..., description="Unique Meta message ID (wamid.XXX) for idempotency")
    from_: str = Field(..., alias="from", description="Sender WhatsApp ID / phone digits")
    timestamp: str
    type: str = "text"
    text: Optional[WhatsAppTextMessage] = None

    @property
    def sender_e164(self) -> str:
        """Converts raw sender digits into strict E.164 format."""
        raw = self.from_
        if not raw.startswith("+"):
            return f"+{raw}"
        return raw


class WhatsAppContact(BaseModel):
    wa_id: str
    profile: Optional[Dict[str, Any]] = None


class WhatsAppValue(BaseModel):
    messaging_product: str = "whatsapp"
    metadata: Optional[Dict[str, Any]] = None
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessageItem]] = None


class WhatsAppChange(BaseModel):
    field: str
    value: WhatsAppValue


class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]


class WhatsAppWebhookPayload(BaseModel):
    object: Optional[str] = "whatsapp_business_account"
    entry: List[WhatsAppEntry]


class InboundMessageDetail(BaseModel):
    """Normalized internal representation for message processing."""
    message_id: str
    sender_phone: str
    text_body: str
    timestamp: str
    message_type: str = "text"
    raw_payload: Dict[str, Any]

    @field_validator("sender_phone")
    def validate_e164(cls, v: str) -> str:
        return normalize_to_e164(v)
