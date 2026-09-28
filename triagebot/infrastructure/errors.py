from pathlib import Path

from ..application.errors import TriageError


class TicketFileNotFound(TriageError):
    def __init__(self, path: Path) -> None:
        super().__init__(f"Ticket file not found: {path}")


class InvalidTicketJson(TriageError):
    def __init__(self, error: Exception) -> None:
        super().__init__(f"Invalid JSON in ticket file: {error}")


class InvalidTicketList(TriageError):
    def __init__(self) -> None:
        super().__init__("Ticket file must contain a JSON list.")


class TicketReadError(TriageError):
    def __init__(self, path: Path, error: Exception) -> None:
        super().__init__(f"Could not read ticket file {path}: {error}")


class OutputWriteError(TriageError):
    def __init__(self, path: Path, error: Exception) -> None:
        super().__init__(f"Could not write {path}: {error}")
