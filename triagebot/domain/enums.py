"""The allowed values used by tickets, analyses and escalation."""

from enum import StrEnum


class Category(StrEnum):
    BUG = "bug"
    PAYMENT = "payment"
    ACCOUNT = "account"
    SUGGESTION = "suggestion"
    TOXICITY = "toxicity"
    OTHER = "other"


class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Status(StrEnum):
    OK = "ok"
    TO_CHECK = "to_check"


class Escalation(StrEnum):
    HUMAN_REVIEW = "human review"
    MODERATION = "moderation team"
    SUPPORT_LEAD = "support lead"
    STANDARD = "standard support"


class ReviewReason(StrEnum):
    INVALID_TICKET = "Empty or invalid ticket"
    PROMPT_INJECTION = "Possible attempt to manipulate the bot"
    ANALYSIS_FAILED = "Analysis failed after two invalid responses"
    MODEL_UNAVAILABLE = "Ollama call failed; human review needed"
    DRAFT_FAILED = "Draft unavailable; human review needed"

