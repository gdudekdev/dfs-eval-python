"""Errors shared by the application and its adapters."""


class TriageError(Exception):
    """Base class for errors that the CLI can display."""

class ModelConnectionError(TriageError):
    def __init__(self, error: Exception) -> None:
        super().__init__(f"Ollama is not running or cannot be reached: {error}")


class ModelRequestError(TriageError):
    def __init__(self, error: Exception) -> None:
        super().__init__(f"Ollama request failed: {error}")


class InvalidModelResponse(TriageError):
    def __init__(self) -> None:
        super().__init__("Ollama returned a response without text content")


class ConflictingPaths(TriageError):
    def __init__(self) -> None:
        super().__init__("Input, result and report paths must be different.")
