from typing import NamedTuple
from enum import StrEnum
import datetime


class CandleInterval(StrEnum):
    Minutes5 = "minutes5"
    Hourly = "hourly"
    Daily = "daily"


class Candle(NamedTuple):
    securityCode: str  # delete?
    dateTime: datetime.datetime
    openPrice: float
    highPrice: float
    lowPrice: float
    closePrice: float
    volume: float
