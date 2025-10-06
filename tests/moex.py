import datetime
from typing import NamedTuple


class TimeRange(NamedTuple):
    startYear:     int
    startQuarter:  int
    finishYear:    int
    finishQuarter: int


def quarterSecurityCodes(name: str, tr: TimeRange) -> list[str]:
    res = []
    for year in range(tr.startYear, tr.finishYear+1):
        for quarter in range(0, 4):
            if year == tr.startYear:
                if quarter < tr.startQuarter:
                    continue
            if year == tr.finishYear:
                if quarter > tr.finishQuarter:
                    break
            res.append(f"{name}-{3+quarter*3}.{year % 100:02}")
    return res


def isMainFortsSession(d: datetime.datetime) -> bool:
    return d.hour >= 10 and d.hour <= 18
