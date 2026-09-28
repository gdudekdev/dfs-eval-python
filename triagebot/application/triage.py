"""A small workflow: filter, reuse a duplicate, or analyze one ticket."""

from dataclasses import replace

from ..domain.enums import Escalation, ReviewReason, Status
from ..domain.models import Ticket, TicketInput, TriageResult
from ..domain.rules import escalation_for, looks_like_prompt_injection
from .errors import InvalidModelResponse, ModelRequestError
from .model import TicketModel


def needs_model(inputs: list[TicketInput]) -> bool:
    for source in inputs:
        if source.ticket is not None and not looks_like_prompt_injection(source.ticket.message):
            return True
    return False


def review_result(source: TicketInput, reason: ReviewReason) -> TriageResult:
    return TriageResult(
        source=source,
        status=Status.TO_CHECK,
        escalation=Escalation.HUMAN_REVIEW,
        reason=reason,
    )


def analyze_ticket(source: TicketInput, ticket: Ticket, model: TicketModel) -> TriageResult:
    try:
        analysis = model.analyze(ticket)
    except ModelRequestError:
        return review_result(source, ReviewReason.MODEL_UNAVAILABLE)
    if analysis is None:
        return review_result(source, ReviewReason.ANALYSIS_FAILED)

    result = TriageResult(
        source=source,
        status=Status.OK,
        escalation=escalation_for(analysis),
        analysis=analysis,
    )
    try:
        result.draft = model.draft_reply(ticket, analysis)
    except (ModelRequestError, InvalidModelResponse):
        result.draft_error = ReviewReason.DRAFT_FAILED
    return result


def process_ticket(
    source: TicketInput,
    model: TicketModel,
    seen: dict[tuple[str, str], TriageResult],
) -> TriageResult:
    ticket = source.ticket
    if ticket is None:
        return review_result(source, ReviewReason.INVALID_TICKET)

    key = (ticket.player, ticket.message)
    if key in seen:
        original = seen[key]
        first_ticket = original.source.ticket
        assert first_ticket is not None  # Only valid tickets enter the duplicate cache.
        return replace(original, source=source, duplicate_of=first_ticket.id)

    if looks_like_prompt_injection(ticket.message):
        result = review_result(source, ReviewReason.PROMPT_INJECTION)
    else:
        result = analyze_ticket(source, ticket, model)
    seen[key] = result
    return result


def process_tickets(inputs: list[TicketInput], model: TicketModel) -> list[TriageResult]:
    results: list[TriageResult] = []
    seen: dict[tuple[str, str], TriageResult] = {}
    for source in inputs:
        results.append(process_ticket(source, model, seen))
    return results
