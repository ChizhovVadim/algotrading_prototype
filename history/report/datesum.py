import datetime
from typing import NamedTuple


class DateSum(NamedTuple):
    "Доходность торговой системы за один день"
    Date: datetime.date
    Sum: float
