import argparse
from pathlib import Path

from ollama import Client

from ..application.errors import ConflictingPaths, TriageError
from ..application.triage import needs_model, process_tickets
from ..config import (
    AppConfig, DEFAULT_INPUT, DEFAULT_MODEL, DEFAULT_OUTPUT, DEFAULT_REPORT,
    OLLAMA_HOST, OLLAMA_TIMEOUT_SECONDS,
)
from ..infrastructure.files import load_tickets, save_results, write_text
from ..infrastructure.ollama_client import OllamaTicketModel
from .report import dashboard, markdown_report
from .text import (
    CLI_DESCRIPTION, ERROR_PREFIX, INPUT_HELP, MODEL_HELP,
    OUTPUT_HELP, REPORT_HELP, SAVED_MESSAGE,
)


class CliArguments(argparse.Namespace):
    input: Path
    output: Path
    report: Path
    model: str


def parse_arguments(argv: list[str] | None = None) -> AppConfig:
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)

    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help=INPUT_HELP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=OUTPUT_HELP)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help=REPORT_HELP)
    parser.add_argument("--model", default=DEFAULT_MODEL, help=MODEL_HELP)

    args = CliArguments()

    parser.parse_args(argv, namespace=args)
    paths = {args.input.resolve(), args.output.resolve(), args.report.resolve()}

    if len(paths) != 3:
        raise ConflictingPaths()
    
    return AppConfig(args.input, args.output, args.report, args.model)


def run(config: AppConfig) -> None:
    inputs = load_tickets(config.input_path)
    client = Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT_SECONDS)
    model = OllamaTicketModel(model_name=config.model_name, client=client)

    if needs_model(inputs):
        model.check_connection()

    results = process_tickets(inputs=inputs, model=model)

    save_results(results=results, path=config.output_path)
    write_text(path=config.report_path, text=markdown_report(results))

    print(dashboard(results))
    print(SAVED_MESSAGE.format(output=config.output_path, report=config.report_path))


def main(argv: list[str] | None = None) -> int:
    try:
        run(parse_arguments(argv))
    except TriageError as error:
        print(ERROR_PREFIX + str(error))
        return 1
    return 0
