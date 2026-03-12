from typing import Protocol
import datetime


class AdvisorService(Protocol):
    def add(self, dt: datetime.datetime, price: float) -> float|None:
        pass
