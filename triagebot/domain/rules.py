"""Input validation and deterministic escalation decisions."""

from pydantic import ValidationError

from .enums import Category, Escalation
from .models import Analysis, Ticket, TicketInput


def parse_ticket(raw: object) -> TicketInput:
    raw_id = raw.get("id") if isinstance(raw, dict) else None
    ticket_id = raw_id if type(raw_id) is int else None
    try:
        ticket = Ticket.model_validate(raw)
    except ValidationError:
        return TicketInput(original=raw, ticket=None, ticket_id=ticket_id)
    if not ticket.player.strip() or not ticket.message.strip():
        return TicketInput(original=raw, ticket=None, ticket_id=ticket_id)
    return TicketInput(original=raw, ticket=ticket, ticket_id=ticket.id)


def parse_analysis(text: str) -> Analysis | None:
    try:
        return Analysis.model_validate_json(text)
    except ValidationError:
        return None


def looks_like_prompt_injection(message: str) -> bool:
    """A narrow rule; unknown phrasings can still require human review."""
    lower = message.lower()
    return ("ignore" in lower and "instruction" in lower) or (
        "classe ce ticket" in lower and "urgence" in lower
    )


def escalation_for(analysis: Analysis) -> Escalation:
    if analysis.category == Category.TOXICITY:
        return Escalation.MODERATION
    if analysis.category == Category.PAYMENT and analysis.severity >= 4:
        return Escalation.SUPPORT_LEAD
    return Escalation.STANDARD
