# TriageBot

A Python CLI that uses a local Ollama model to classify support tickets, draft replies and generate a report.

## Requirements

- Python 3.14
- Ollama installed
- Windows with Git Bash for the commands below

## Installation

Open Git Bash in the project folder and run:

```bash
py -3.14 -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt

ollama pull llama3.2:3b
```

## Run

Make sure Ollama is running. If needed, start it in another terminal:

```bash
ollama serve
```

Then run the application from the project folder:

```bash
python -m triagebot
```

The program reads `tickets.json`, displays a dashboard and creates:

- `results.json`: original tickets, analyses and reply drafts.
- `report.md`: summary, escalations and tickets requiring review.

To choose different files or another installed model:

```bash
python -m triagebot \
    --input tickets.json \
    --output results.json \
    --report report.md \
    --model llama3.2:3b
```

When opening a new terminal, reactivate the virtual environment before running the project:

```bash
source .venv/Scripts/activate
```