import datetime
import calendar

def lastDayOfMonth(d: datetime.datetime):
    _, days = calendar.monthrange(d.year, d.month)
    return datetime.datetime(d.year, d.month, days)

def lastDayOfYear(d: datetime.datetime):
    return datetime.datetime(d.year, 12, 31)

def isNewDayStarted(l: datetime.datetime, r: datetime.datetime)-> bool:
    return l.date() != r.date()

def isMainFortsSession(d: datetime.datetime)-> bool:
    return d.hour >= 10 and d.hour <= 18

def isNewFortsDateStarted(l: datetime.datetime, r: datetime.datetime)-> bool:
    return isMainFortsSession(l) and (not isMainFortsSession(r) or l.date() != r.date())

_warDate = datetime.date(2022,2,25)

def afterLongHoliday(l: datetime.datetime, r: datetime.datetime)-> bool:
    startDate = l.date()
    finishDate = r.date()
    if startDate == finishDate:
        return False
    # приостановка торгов, выйти заранее невозможно
    if startDate == _warDate:
        return False
    d = startDate+datetime.timedelta(days=1)
    while d < finishDate:
        # В промежутке между startDate и finishDate был 1 не выходной, значит праздник
        # На праздники закрываем позиции. прибыль/убыток гепа выкидиваем
        if d.weekday() not in [5,6]:
            return True
        d += datetime.timedelta(days=1)
    return False
