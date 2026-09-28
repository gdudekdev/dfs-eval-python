from abc import ABC, abstractmethod

from ..domain.models import Analysis, Ticket


class TicketModel(ABC):
    @abstractmethod
    def check_connection(self) -> None:
        pass

    @abstractmethod
    def analyze(self, ticket: Ticket) -> Analysis | None:
        pass

    @abstractmethod
    def draft_reply(self, ticket: Ticket, analysis: Analysis) -> str:
        pass
