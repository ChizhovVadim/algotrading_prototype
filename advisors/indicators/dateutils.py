import datetime


def isMainFortsSession(d: datetime.datetime) -> bool:
    return d.hour >= 10 and d.hour <= 18


def isOneDayMainSession(d1: datetime.datetime, d2: datetime.datetime) -> bool:
    return d1.date() == d2.date() and isMainFortsSession(d1) and isMainFortsSession(d2)
