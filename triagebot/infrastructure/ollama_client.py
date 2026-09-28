import json

from httpx import HTTPError
from ollama import ChatResponse, Client, Message, Options, RequestError, ResponseError
from pydantic import ValidationError

from ..application.errors import InvalidModelResponse, ModelConnectionError, ModelRequestError
from ..application.model import TicketModel
from ..domain.models import Analysis, Ticket
from ..domain.rules import parse_analysis
from .model_config import ANALYSIS_PROMPT, DRAFT_PROMPT, MAX_ATTEMPTS, MAX_DRAFT_LENGTH


class OllamaTicketModel(TicketModel):
    def __init__(self, model_name: str, client: Client) -> None:
        self.model_name = model_name
        self.client = client

    def check_connection(self) -> None:
        try:
            self.client.list()
        except (ConnectionError, HTTPError, RequestError, ResponseError, ValidationError, json.JSONDecodeError) as error:
            raise ModelConnectionError(error) from error

    def call_model(self, messages: list[Message], structured: bool = False) -> str:
        try:
            response: ChatResponse = self.client.chat(
                model=self.model_name,
                messages=messages,
                options=Options(temperature=0),
                format=Analysis.model_json_schema() if structured else None,
                stream=False,
            )
        except (ConnectionError, HTTPError, RequestError, ResponseError) as error:
            raise ModelRequestError(error) from error
        except (ValidationError, json.JSONDecodeError) as error:
            raise InvalidModelResponse() from error
        content = response.message.content
        if content is None or not content.strip():
            raise InvalidModelResponse()
        return content

    def analyze(self, ticket: Ticket) -> Analysis | None:
        messages: list[Message] = [
            Message(role="system", content=ANALYSIS_PROMPT),
            Message(role="user", content=ticket.model_dump_json()),
        ]
        for _ in range(MAX_ATTEMPTS):
            try:
                analysis = parse_analysis(self.call_model(messages, structured=True))
                if analysis is not None:
                    return analysis
            except InvalidModelResponse:
                continue
        return None

    def draft_reply(self, ticket: Ticket, analysis: Analysis) -> str:
        request = json.dumps({"ticket": ticket.message, "analysis": analysis.model_dump(mode="json")})
        messages: list[Message] = [
            Message(role="system", content=DRAFT_PROMPT),
            Message(role="user", content=request),
        ]
        return self.call_model(messages).strip()[:MAX_DRAFT_LENGTH]