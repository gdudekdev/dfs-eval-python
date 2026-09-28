"""Runtime settings. Defaults live here; adapters receive explicit values."""

from dataclasses import dataclass
from pathlib import Path

DEFAULT_INPUT = Path("tickets.json")
DEFAULT_OUTPUT = Path("results.json")
DEFAULT_REPORT = Path("report.md")
DEFAULT_MODEL = "llama3.2:3b"
OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_TIMEOUT_SECONDS = 120.0


@dataclass(frozen=True)
class AppConfig:
    input_path: Path
    output_path: Path
    report_path: Path
    model_name: str
