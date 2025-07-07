import datetime
from typing import NamedTuple, Any, Callable

from domaintypes import Candle

_displayDateTimeLayout = "%d.%m.%Y %H:%M"


class Advice(NamedTuple):
    securityCode: str
    dateTime: datetime.datetime
    price: float
    position: float
    details: Any

    def __str__(self):
        return f"{self.securityCode} {self.dateTime.strftime(_displayDateTimeLayout)} {self.price} {self.position} {self.details}"


Advisor = Callable[[Candle], Advice | None]
