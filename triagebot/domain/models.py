"""Validated business data, independent of files and Ollama."""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from .enums import Category, Escalation, ReviewReason, Sentiment, Status


class Ticket(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")

    id: int
    player: str = Field(min_length=1)
    message: str = Field(min_length=1)


class Analysis(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", str_strip_whitespace=True)

    category: Category
    severity: int = Field(ge=1, le=5)
    sentiment: Sentiment
    summary: str = Field(min_length=1)


@dataclass
class TicketInput:
    original: object
    ticket: Ticket | None
    ticket_id: int | None

    @property
    def label(self) -> str:
        return str(self.ticket_id) if self.ticket_id is not None else "?"


@dataclass
class TriageResult:
    source: TicketInput
    status: Status
    escalation: Escalation
    analysis: Analysis | None = None
    draft: str | None = None
    reason: ReviewReason | None = None
    draft_error: ReviewReason | None = None
    duplicate_of: int | None = None
