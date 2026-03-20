from typing import NamedTuple
import datetime
from domain.model.broker import Portfolio, Security


class Signal(NamedTuple):
    name: str
    deadline: datetime.datetime
    price: float
    value: float


class PlannedPosition(NamedTuple):
    portfolio: Portfolio
    security: Security
    planned: int
