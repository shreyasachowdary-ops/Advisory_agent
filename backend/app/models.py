from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Audience(str, Enum):
    PARENT = "parent"
    TEACHER = "teacher"


class AgeBand(str, Enum):
    TWO_YEARS = "2_years"
    THREE_YEARS = "3_years"
    FOUR_YEARS = "4_years"
    FIVE_YEARS = "5_years"


class RiskLevel(str, Enum):
    NORMAL = "normal"
    REFERRAL = "referral"
    URGENT = "urgent"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    audience: Audience = Audience.PARENT
    age_band: AgeBand = AgeBand.FOUR_YEARS
    language: Literal["en"] = "en"


class SourceCitation(BaseModel):
    title: str
    url: str
    chunk_id: str


class ChatResponse(BaseModel):
    answer: str
    risk_level: RiskLevel
    sources: list[SourceCitation] = Field(default_factory=list)
    suggested_follow_up: str | None = None
    requires_human_review: bool = False


class FeedbackRequest(BaseModel):
    rating: Literal["helpful", "not_helpful", "unsafe"]


class SafeguardingConfirmRequest(BaseModel):
    category: str
    severity: Literal["low", "medium", "high", "critical"]
    user_summary: str = Field(..., max_length=2000)
    user_confirmed: bool = False


class HealthResponse(BaseModel):
    status: str
    ollama: bool
    kb_version: str
