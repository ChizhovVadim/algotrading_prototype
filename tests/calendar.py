import datetime

_warDate = datetime.date(2022, 2, 25)


def afterLongHoliday(l: datetime.datetime, r: datetime.datetime) -> bool:
    """Хотим на длинные выходные сокращать или закрывать позиции"""

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
        if d.weekday() not in [5, 6]:
            return True
        d += datetime.timedelta(days=1)
    return False
