import datetime
from dataclasses import dataclass


@dataclass
class DayCandle:
    date: datetime.date
    openPrice: float
    highPrice: float
    lowPrice: float
    closePrice: float


class DayCandleAccumulator:
    def __init__(self):
        self._dayCandles: list[DayCandle] = []

    def add(self, dt, v):
        if len(self._dayCandles) == 0 or dt.date() != self._dayCandles[-1].date:
            newDay = DayCandle(
                date=dt.date(),
                openPrice=v,
                highPrice=v,
                lowPrice=v,
                closePrice=v,
            )
            self._dayCandles.append(newDay)
        else:
            last = self._dayCandles[-1]
            last.highPrice = max(last.highPrice, v)
            last.lowPrice = min(last.lowPrice, v)
            last.closePrice = v
