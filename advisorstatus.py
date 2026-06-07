import collections
import datetime
from typing import NamedTuple


class Signal(NamedTuple):
    datetime: datetime.datetime
    price: float
    position: float

    def __str__(self) -> str:
        return f"{self.datetime.strftime("%d.%m.%Y %H:%M")} {self.price} {self.position:.4f}"


def advisorStatusUsecase(
    candleStorage,
    advisor,
    security: str,
    count: int,
):
    advices = collections.deque(maxlen=count)
    for candle in candleStorage.read(security):
        if not advisor.add(candle.dateTime, candle.closePrice):
            continue
        pos = advisor.value()
        if len(advices) == 0 or advices[-1].position != pos:
            advices.append(Signal(candle.dateTime, candle.closePrice, pos))

    print(security)
    for advice in advices:
        print(advice)
