from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    TASK_LOG = "TASK_LOG"
    STATUS_QUERY = "STATUS_QUERY"
    UNKNOWN = "UNKNOWN"


class ExtractedTask(BaseModel):
    description: str = Field(..., description="Clear summary of what was worked on")
    duration_minutes: Optional[int] = Field(None, description="Estimated time spent in minutes")
    category: Optional[str] = Field("General", description="Category: e.g. Development, Meeting, Support, Bugfix, Admin")
    status: str = Field("COMPLETED", description="Status of task: COMPLETED, IN_PROGRESS, or BLOCKED")


class ParsedEmployeeMessage(BaseModel):
    """
    JSON Schema structured output for employee daily task logging.
    """
    intent: IntentType = Field(IntentType.TASK_LOG, description="Identified primary user intent")
    tasks: List[ExtractedTask] = Field(default_factory=list, description="List of tasks performed or logged in message")
    notes: Optional[str] = Field(None, description="Additional context or blocker details")
    confidence_score: float = Field(0.95, ge=0.0, le=1.0, description="Model confidence score in intent parsing")
    reply_message: str = Field(..., description="Friendly, clear WhatsApp acknowledgment message to reply back to employee")
