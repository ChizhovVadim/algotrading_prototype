import datetime
import functools
import statistics
import math
from typing import NamedTuple

from .import dateutils
from .datesum import DateSum

displayDateLayout = "%d.%m.%Y"

class DrawdownInfo(NamedTuple):
    HighEquityDate: datetime.date
    MaxDrawdown: float
    LongestDrawdown: int
    CurrentDrawdown: float
    CurrentDrawdownDays: int


class HprStatistcs(NamedTuple):
    MonthHpr: float
    StDev: float
    AVaR: float
    DayHprs: list[DateSum]
    MonthHprs: list[DateSum]
    YearHprs: list[DateSum]
    DrawdownInfo: DrawdownInfo


def computeHprStatistcs(hprs: list[DateSum]) -> HprStatistcs:
    "По дневным доходностям формирует статистику"

    # TODO сразу преобразовать в log?
    total_hpr = functools.reduce(lambda x, y: x*y.Sum, hprs, 1.0)
    month_hpr = total_hpr ** (22.0/len(hprs))
    stdev = statistics.stdev((math.log(x.Sum) for x in hprs))
    return HprStatistcs(
        MonthHpr=month_hpr,
        StDev=stdev,
        AVaR=calcAvar(hprs),
        DayHprs=hprs,
        # ф-ция datetime для date объектов
        MonthHprs=hprsByPeriod(hprs, dateutils.lastDayOfMonth),
        # ф-ция datetime для date объектов
        YearHprs=hprsByPeriod(hprs, dateutils.lastDayOfYear),
        DrawdownInfo=compute_drawdown_info(hprs),
    )


def calcAvar(hprs: list[DateSum]) -> float:
    hprs = [x.Sum for x in hprs]
    hprs.sort()
    hprs = hprs[:len(hprs)//20]
    return statistics.mean(hprs)


def hprsByPeriod(hprs: list[DateSum], period) -> list[DateSum]:
    result = []
    lastDate = None
    lastHpr = 1.0
    for hpr in hprs:
        curPeriod = period(hpr.Date)
        if lastDate is not None and period(lastDate) != curPeriod:
            result.append(DateSum(lastDate, lastHpr))
            lastHpr = 1.0
        lastDate = curPeriod
        lastHpr *= hpr.Sum
    if lastDate is not None:
        result.append(DateSum(lastDate, lastHpr))
    return result


def compute_drawdown_info(hprs: list[DateSum]) -> DrawdownInfo:
    currentSum = 0.0
    maxSum = 0.0
    longestDrawdown = 0
    currentDrawdownDays = 0
    maxDrawdown = 0.0
    highEquityDate = hprs[0].Date

    for hpr in hprs:
        currentSum += math.log(hpr.Sum)
        if currentSum > maxSum:
            maxSum = currentSum
            highEquityDate = hpr.Date
        curDrawdown = currentSum - maxSum
        if curDrawdown < maxDrawdown:
            maxDrawdown = curDrawdown
        currentDrawdownDays = (hpr.Date - highEquityDate).days
        if currentDrawdownDays > longestDrawdown:
            longestDrawdown = currentDrawdownDays

    return DrawdownInfo(
        HighEquityDate=highEquityDate,
        MaxDrawdown=math.exp(maxDrawdown),
        LongestDrawdown=longestDrawdown,
        CurrentDrawdown=math.exp(currentSum-maxSum),
        CurrentDrawdownDays=currentDrawdownDays,
    )


def printReport(r: HprStatistcs):
    print(f"Ежемесячная доходность {hprDisplay(r.MonthHpr):.1f}%")
    print(
        f"Среднеквадратичное отклонение доходности за день {r.StDev*100:.1f}%")
    print(
        f"Средний убыток в день среди 5% худших дней {hprDisplay(r.AVaR):.1f}%")
    printDrawdownInfo(r.DrawdownInfo)
    print("Доходности по дням")
    printHprs(r.DayHprs[-20:])
    print("Доходности по месяцам")
    printHprs(r.MonthHprs)
    print("Доходности по годам")
    printHprs(r.YearHprs)


def printHprs(hprs: list[DateSum]):
    for item in hprs:
        print(
            f"{item.Date.strftime(displayDateLayout)} {hprDisplay(item.Sum):>8,.1f}%")


def printDrawdownInfo(data: DrawdownInfo):
    print(f"Максимальная просадка {hprDisplay(data.MaxDrawdown):.1f}%")
    print(f"Продолжительная просадка {data.LongestDrawdown} дн.")
    print(
        f"Текущая просадка {hprDisplay(data.CurrentDrawdown):.1f}% {data.CurrentDrawdownDays} дн.")
    print(
        f"Дата максимума эквити {data.HighEquityDate.strftime(displayDateLayout)}")


def hprDisplay(hpr: float) -> float:
    return (hpr-1.0)*100.0
