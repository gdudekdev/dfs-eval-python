"""Build the dashboard and Markdown report from typed triage results."""

from collections import Counter

from ..domain.enums import Category, Escalation, Status
from ..domain.models import TriageResult

TOP_TICKET_COUNT = 3


def dashboard(results: list[TriageResult]) -> str:
    sections = [
        _format_ticket_counts(results),
        _format_category_counts(results),
        _format_average_severity(results),
        _format_top_tickets(results),
    ]
    return "\n".join(sections)


def markdown_report(results: list[TriageResult]) -> str:
    summary = "## Summary\n\n```\n" + dashboard(results) + "\n```"
    escalations = _markdown_section("Escalated tickets", _escalation_entries(results))
    reviews = _markdown_section("Tickets to check", _review_entries(results))

    sections = ["# TriageBot report", summary, escalations, reviews]
    return "\n\n".join(sections) + "\n"


def _format_ticket_counts(results: list[TriageResult]) -> str:
    analyzed_count = 0
    review_count = 0

    for result in results:
        if result.analysis is not None:
            analyzed_count += 1
        if result.status == Status.TO_CHECK:
            review_count += 1

    return (
        f"Tickets: {len(results)} | "
        f"Analyzed: {analyzed_count} | "
        f"To check: {review_count}"
    )


def _format_category_counts(results: list[TriageResult]) -> str:
    counts: Counter[Category] = Counter()
    for result in results:
        if result.analysis is not None:
            counts[result.analysis.category] += 1

    lines: list[str] = []
    for category in Category:
        lines.append(f"  {category.value}: {counts[category]}")
    return "\n".join(lines)


def _format_average_severity(results: list[TriageResult]) -> str:
    severities: list[int] = []
    for result in results:
        if result.analysis is not None:
            severities.append(result.analysis.severity)

    average = 0.0
    if severities:
        average = sum(severities) / len(severities)
    return f"Average severity: {average:.2f}/5"


def _severity_of(result: TriageResult) -> int:
    if result.analysis is None:
        return 0
    return result.analysis.severity


def _format_top_tickets(results: list[TriageResult]) -> str:
    analyzed: list[TriageResult] = []
    for result in results:
        if result.analysis is not None:
            analyzed.append(result)

    ranked = sorted(analyzed, key=_severity_of, reverse=True)
    entries: list[str] = []
    for result in ranked[:TOP_TICKET_COUNT]:
        entries.append(f"#{result.source.label} ({_severity_of(result)}/5)")

    if not entries:
        return f"Top {TOP_TICKET_COUNT}: none"
    return f"Top {TOP_TICKET_COUNT}: " + ", ".join(entries)


def _escalation_entries(results: list[TriageResult]) -> list[str]:
    entries: list[str] = []
    for result in results:
        if result.status == Status.TO_CHECK:
            continue
        if result.escalation == Escalation.STANDARD or result.analysis is None:
            continue

        entries.append(
            f"#{result.source.label}: "
            f"{result.escalation.value} — {result.analysis.summary}"
        )
    return entries


def _review_entries(results: list[TriageResult]) -> list[str]:
    entries: list[str] = []
    for result in results:
        if result.status == Status.TO_CHECK and result.reason is not None:
            entries.append(f"#{result.source.label}: {result.reason.value}")
        if result.draft_error is not None:
            entries.append(f"#{result.source.label}: {result.draft_error.value}")
    return entries


def _markdown_section(title: str, entries: list[str]) -> str:
    lines = [f"## {title}", ""]
    if not entries:
        lines.append("- None")
    else:
        for entry in entries:
            lines.append(f"- {entry}")
    return "\n".join(lines)
