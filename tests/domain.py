import datetime
from typing import NamedTuple


class DateSum(NamedTuple):
    "Доходность торговой системы за один день"
    date: datetime.date
    sum: float
