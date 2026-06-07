from typing import NamedTuple
import datetime
from broker.model import Portfolio, Security


class Signal(NamedTuple):
    name: str
    deadline: datetime.datetime
    price: float
    value: float


class PlannedPosition(NamedTuple):
    portfolio: Portfolio
    security: Security
    planned: int


class UserCmd:
    pass


class ExitUserCmd(UserCmd):
    pass


class CheckStatusUserCmd(UserCmd):
    pass
