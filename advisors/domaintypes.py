import datetime
from typing import NamedTuple, Any, Callable

from domaintypes import Candle

_displayDateTimeLayout = "%d.%m.%Y %H:%M"


class Advice(NamedTuple):
    SecurityCode: str
    DateTime: datetime.datetime
    Price: float
    Position: float
    Details: Any

    def __str__(self):
        return f"{self.SecurityCode} {self.DateTime.strftime(_displayDateTimeLayout)} {self.Price} {self.Position} {self.Details}"


Advisor = Callable[[Candle], Advice | None]

IndicatorFunc = Callable[[Candle], float]
