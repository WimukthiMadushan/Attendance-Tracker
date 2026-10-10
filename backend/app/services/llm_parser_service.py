import json
import logging
import re
from datetime import datetime
from typing import Optional
import httpx

from app.core.config import settings
from app.schemas.ai_parser import ParsedEmployeeMessage, IntentType, ExtractedTask

logger = logging.getLogger("attendance_tracker.llm")

SYSTEM_INSTRUCTION = """You are an AI assistant for an enterprise WhatsApp attendance and daily task tracking system.
Your job is to analyze incoming WhatsApp messages from employees and extract structured data according to the JSON schema.

Classify the intent into one of:
- CHECK_IN: Employee reporting they started work or arrived.
- CHECK_OUT: Employee reporting end of day or leaving.
- TASK_LOG: Employee submitting what tasks they worked on.
- CHECK_OUT_WITH_TASKS: Employee clocking out AND listing the day's completed tasks.
- LEAVE_REQUEST: Employee informing they are on leave, sick, or taking time off.
- STATUS_QUERY: Employee asking for their tracked hours, attendance status, or summary.
- UNKNOWN: Irrelevant or ambiguous message.

Rules:
1. Extract any tasks mentioned, including brief descriptions, estimated minutes spent (if discernable, else 60), category, and status.
2. Formulate a polite, professional, and concise WhatsApp reply message (reply_message) confirming their action.
3. Return strict JSON matching the schema with NO markdown wrapping or preamble.
"""


class LLMParserService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL

    async def parse_message(self, message_text: str, sender_phone: str) -> ParsedEmployeeMessage:
        """
        Parses an incoming employee WhatsApp message into structured data.
        Falls back to rule-based heuristic parsing if API key is a placeholder or LLM request fails.
        """
        # If API key is still the placeholder or unset, use smart heuristic fallback
        if not self.api_key or "placeholder" in self.api_key.lower() or "xxxx" in self.api_key.lower():
            logger.info("Using heuristic parser (placeholder API key detected).")
            return self._heuristic_parse(message_text)

        try:
            if self.provider == "gemini":
                return await self._parse_with_gemini(message_text)
            elif self.provider == "openai":
                return await self._parse_with_openai(message_text)
            else:
                return self._heuristic_parse(message_text)
        except Exception as e:
            logger.error(f"Error calling LLM provider {self.provider}: {e}. Falling back to heuristic parser.")
            return self._heuristic_parse(message_text)

    async def _parse_with_gemini(self, text: str) -> ParsedEmployeeMessage:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = f"{SYSTEM_INSTRUCTION}\n\nEmployee Message:\n\"{text}\"\n\nJSON Output:"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1,
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_dict = json.loads(raw_json)
            return ParsedEmployeeMessage(**parsed_dict)

    async def _parse_with_openai(self, text: str) -> ParsedEmployeeMessage:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model if self.model else "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": text}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_json = data["choices"][0]["message"]["content"]
            parsed_dict = json.loads(raw_json)
            return ParsedEmployeeMessage(**parsed_dict)

    def _heuristic_parse(self, text: str) -> ParsedEmployeeMessage:
        """
        High-fidelity heuristic fallback when offline or during initial configuration.
        """
        lower = text.lower().strip()
        now_time = datetime.now().strftime("%H:%M")

        if any(w in lower for w in ["check in", "checking in", "clock in", "start work", "arrived", "gm", "good morning", "started shift"]):
            return ParsedEmployeeMessage(
                intent=IntentType.CHECK_IN,
                check_in_time=now_time,
                tasks=[],
                confidence_score=0.92,
                reply_message=f"Good day! You have been checked in at {now_time}. Have a productive day!",
            )

        has_checkout = any(w in lower for w in ["check out", "checking out", "clock out", "leaving", "bye", "end of day", "eod", "logging off"])
        has_tasks = any(w in lower for w in ["worked on", "completed", "fixed", "meeting", "tasks:", "done:", "1.", "- "])

        if has_checkout and has_tasks:
            tasks = self._extract_tasks_heuristically(text)
            return ParsedEmployeeMessage(
                intent=IntentType.CHECK_OUT_WITH_TASKS,
                check_out_time=now_time,
                tasks=tasks,
                confidence_score=0.89,
                reply_message=f"Checked out at {now_time}. Logged {len(tasks)} daily task(s). Great job today!",
            )

        if has_checkout:
            return ParsedEmployeeMessage(
                intent=IntentType.CHECK_OUT,
                check_out_time=now_time,
                tasks=[],
                confidence_score=0.90,
                reply_message=f"You have been checked out at {now_time}. Rest well!",
            )

        if any(w in lower for w in ["leave", "sick", "vacation", "off today", "not feeling well", "unwell", "emergency leave"]):
            return ParsedEmployeeMessage(
                intent=IntentType.LEAVE_REQUEST,
                notes=text,
                tasks=[],
                confidence_score=0.88,
                reply_message="Your leave notification has been logged and forwarded to HR.",
            )

        # Default to Task Log if lines or bullet points detected
        tasks = self._extract_tasks_heuristically(text)
        return ParsedEmployeeMessage(
            intent=IntentType.TASK_LOG,
            tasks=tasks,
            confidence_score=0.85,
            reply_message=f"Logged {len(tasks)} task(s) for your daily report. Thank you!",
        )

    def _extract_tasks_heuristically(self, text: str) -> list[ExtractedTask]:
        lines = [line.strip("- *#1234567890.").strip() for line in text.split("\n") if line.strip()]
        tasks: list[ExtractedTask] = []
        for line in lines:
            if len(line) < 4:
                continue
            # Filter greeting / checkout keywords out of single-line task item
            if line.lower() in ["check in", "check out", "eod report", "daily tasks", "today's update"]:
                continue
            tasks.append(
                ExtractedTask(
                    description=line,
                    duration_minutes=60,
                    category="General",
                    status="COMPLETED"
                )
            )
        if not tasks:
            tasks.append(
                ExtractedTask(
                    description=text.strip(),
                    duration_minutes=60,
                    category="General",
                    status="COMPLETED"
                )
            )
        return tasks


llm_parser_service = LLMParserService()
