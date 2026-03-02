from typing import NamedTuple, Protocol
from collections.abc import Generator
from enum import StrEnum
import datetime


class CandleInterval(StrEnum):
    Minutes5 = "minutes5"
    Hourly = "hourly"
    Daily = "daily"


class Candle(NamedTuple):
    # interval: str
    securityCode: str
    dateTime: datetime.datetime
    openPrice: float
    highPrice: float
    lowPrice: float
    closePrice: float
    volume: float


class CandleStorage(Protocol):
    def read(self, securityCode: str) -> Generator[Candle]:
        pass
