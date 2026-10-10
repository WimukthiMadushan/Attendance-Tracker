import json
import logging
import re
from typing import Optional
import httpx

from app.core.config import settings
from app.schemas.ai_parser import ParsedEmployeeMessage, IntentType, ExtractedTask

logger = logging.getLogger("attendance_tracker.llm")

SYSTEM_INSTRUCTION = """You are an AI assistant for an enterprise WhatsApp daily task tracking system.
Your job is to analyze incoming WhatsApp messages from employees and extract structured task descriptions.

Classify the intent into one of:
- TASK_LOG: Employee submitting what tasks or activities they completed or worked on.
- STATUS_QUERY: Employee asking for their tracked tasks summary.
- UNKNOWN: Irrelevant or ambiguous message.

Rules:
1. Extract any tasks mentioned with clear descriptions, category (Development, Meeting, Support, Admin, Bugfix, etc.), and status.
2. Formulate a polite, professional, and concise WhatsApp reply message (reply_message) confirming their logged tasks.
3. Return strict JSON matching the schema with NO markdown wrapping.
"""


class LLMParserService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL

    async def parse_message(self, message_text: str, sender_phone: str) -> ParsedEmployeeMessage:
        """
        Parses an incoming employee WhatsApp message into structured task data.
        Falls back to rule-based heuristic parsing if API key is a placeholder or LLM request fails.
        """
        if not self.api_key or "placeholder" in self.api_key.lower() or "xxxx" in self.api_key.lower():
            logger.info("Using heuristic task parser (placeholder API key detected).")
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
        prompt = f"{SYSTEM_INSTRUCTION}\n\nEmployee Message:\n{text}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json", "temperature": 0.1},
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return ParsedEmployeeMessage.model_validate_json(raw_text)

    async def _parse_with_openai(self, text: str) -> ParsedEmployeeMessage:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model if "gpt" in self.model else "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": text},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            return ParsedEmployeeMessage.model_validate_json(raw_text)

    def _heuristic_parse(self, text: str) -> ParsedEmployeeMessage:
        """Fast fallback rule-based parser for tasks."""
        lower = text.lower().strip()

        if any(w in lower for w in ["how many tasks", "status", "summary", "my tasks"]):
            return ParsedEmployeeMessage(
                intent=IntentType.STATUS_QUERY,
                tasks=[],
                confidence_score=0.90,
                reply_message="You can view your logged daily tasks in the web dashboard.",
            )

        tasks = self._extract_tasks_heuristically(text)
        return ParsedEmployeeMessage(
            intent=IntentType.TASK_LOG,
            tasks=tasks,
            confidence_score=0.90,
            reply_message=f"Logged {len(tasks)} task(s) to your record. Thank you!",
        )

    def _extract_tasks_heuristically(self, text: str) -> list[ExtractedTask]:
        lines = [line.strip("- *#1234567890.").strip() for line in text.split("\n") if line.strip()]
        tasks: list[ExtractedTask] = []
        for line in lines:
            if len(line) < 4:
                continue
            if line.lower() in ["daily tasks", "today's update", "tasks:", "done:", "eod"]:
                continue
            tasks.append(
                ExtractedTask(
                    description=line,
                    duration_minutes=60,
                    category="General",
                    status="COMPLETED",
                )
            )
        if not tasks:
            tasks.append(
                ExtractedTask(
                    description=text.strip(),
                    duration_minutes=60,
                    category="General",
                    status="COMPLETED",
                )
            )
        return tasks


llm_parser_service = LLMParserService()
