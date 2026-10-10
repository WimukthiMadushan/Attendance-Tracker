from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    TASK_LOG = "TASK_LOG"
    CHECK_OUT_WITH_TASKS = "CHECK_OUT_WITH_TASKS"
    LEAVE_REQUEST = "LEAVE_REQUEST"
    STATUS_QUERY = "STATUS_QUERY"
    UNKNOWN = "UNKNOWN"


class ExtractedTask(BaseModel):
    description: str = Field(..., description="Clear summary of what was worked on")
    duration_minutes: Optional[int] = Field(None, description="Estimated time spent in minutes")
    category: Optional[str] = Field("General", description="Category: e.g. Development, Meeting, Support, Bugfix, Admin")
    status: str = Field("COMPLETED", description="Status of task: COMPLETED, IN_PROGRESS, or BLOCKED")


class ParsedEmployeeMessage(BaseModel):
    """
    JSON Schema structured output expected from Gemini / OpenAI.
    """
    intent: IntentType = Field(..., description="Identified primary user intent")
    check_in_time: Optional[str] = Field(None, description="Explicit check-in time if stated (ISO 8601 or HH:MM), otherwise null")
    check_out_time: Optional[str] = Field(None, description="Explicit check-out time if stated (ISO 8601 or HH:MM), otherwise null")
    tasks: List[ExtractedTask] = Field(default_factory=list, description="List of tasks performed or logged in message")
    notes: Optional[str] = Field(None, description="Additional context, blocker details, or leave reasons")
    confidence_score: float = Field(0.95, ge=0.0, le=1.0, description="Model confidence score in intent parsing")
    reply_message: str = Field(..., description="Friendly, clear WhatsApp acknowledgment message to reply back to employee")
