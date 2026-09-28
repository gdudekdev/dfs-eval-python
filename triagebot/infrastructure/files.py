import json
from pathlib import Path

from ..domain.models import TicketInput, TriageResult
from ..domain.rules import parse_ticket
from .errors import (
    InvalidTicketJson, InvalidTicketList, OutputWriteError,
    TicketFileNotFound, TicketReadError,
)


def load_tickets(path: Path) -> list[TicketInput]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise TicketFileNotFound(path) from error
    except (OSError, UnicodeError) as error:
        raise TicketReadError(path, error) from error
    try:
        raw: object = json.loads(text)
    except ValueError as error:
        raise InvalidTicketJson(error) from error
    if not isinstance(raw, list):
        raise InvalidTicketList()
    return [parse_ticket(item) for item in raw]


def serialize_result(result: TriageResult) -> dict[str, object]:
    analysis = result.analysis.model_dump(mode="json") if result.analysis is not None else None
    data: dict[str, object] = {
        "ticket": result.source.original,
        "analysis": analysis,
        "status": result.status.value,
        "escalation": result.escalation.value,
        "draft": result.draft,
    }
    if result.reason is not None:
        data["reason"] = result.reason.value
    if result.draft_error is not None:
        data["draft_error"] = result.draft_error.value
    if result.duplicate_of is not None:
        data["duplicate_of"] = result.duplicate_of
    return data


def write_text(path: Path, text: str) -> None:
    try:
        path.write_text(text, encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise OutputWriteError(path, error) from error


def save_results(results: list[TriageResult], path: Path) -> None:
    data = [serialize_result(result) for result in results]
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")