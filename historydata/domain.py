from typing import NamedTuple
import datetime


class Candle(NamedTuple):
    securityCode: str
    dateTime: datetime.datetime
    openPrice: float
    highPrice: float
    lowPrice: float
    closePrice: float
    volume: float
