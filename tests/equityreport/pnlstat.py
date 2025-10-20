import datetime
import calendar
import functools
import statistics
import math
from typing import NamedTuple

from tests.domain import DateSum

displayDateLayout = "%d.%m.%Y"


class DrawdownInfo(NamedTuple):
    highEquityDate: datetime.date
    maxDrawdown: float
    longestDrawdown: int
    currentDrawdown: float
    currentDrawdownDays: int


class HprStatistcs(NamedTuple):
    monthHpr: float
    stDev: float
    aVaR: float
    dayHprs: list[DateSum]
    monthHprs: list[DateSum]
    yearHprs: list[DateSum]
    drawdownInfo: DrawdownInfo


def computeAndPrint(hprs: list[DateSum]):
    printReport(computeHprStatistcs(hprs))


def computeHprStatistcs(hprs: list[DateSum]) -> HprStatistcs:
    "По дневным доходностям формирует отчет"

    # TODO сразу преобразовать в log?
    total_hpr = functools.reduce(lambda x, y: x*y.sum, hprs, 1.0)
    month_hpr = total_hpr ** (22.0/len(hprs))
    stdev = statistics.stdev((math.log(x.sum) for x in hprs))
    return HprStatistcs(
        monthHpr=month_hpr,
        stDev=stdev,
        aVaR=calcAvar(hprs),
        dayHprs=hprs,
        monthHprs=hprsByPeriod(hprs, lastDayOfMonth),
        yearHprs=hprsByPeriod(hprs, lastDayOfYear),
        drawdownInfo=compute_drawdown_info(hprs),
    )


def calcAvar(hprs: list[DateSum]) -> float:
    hprs = [x.sum for x in hprs]
    hprs.sort()
    hprs = hprs[:len(hprs)//20]
    return statistics.mean(hprs)


def hprsByPeriod(hprs: list[DateSum], period) -> list[DateSum]:
    result = []
    lastDate = None
    lastHpr = 1.0
    for hpr in hprs:
        curPeriod = period(hpr.date)
        if lastDate is not None and period(lastDate) != curPeriod:
            result.append(DateSum(lastDate, lastHpr))
            lastHpr = 1.0
        lastDate = curPeriod
        lastHpr *= hpr.sum
    if lastDate is not None:
        result.append(DateSum(lastDate, lastHpr))
    return result


def compute_drawdown_info(hprs: list[DateSum]) -> DrawdownInfo:
    currentSum = 0.0
    maxSum = 0.0
    longestDrawdown = 0
    currentDrawdownDays = 0
    maxDrawdown = 0.0
    highEquityDate = hprs[0].date

    for hpr in hprs:
        currentSum += math.log(hpr.sum)
        if currentSum > maxSum:
            maxSum = currentSum
            highEquityDate = hpr.date
        curDrawdown = currentSum - maxSum
        if curDrawdown < maxDrawdown:
            maxDrawdown = curDrawdown
        currentDrawdownDays = (hpr.date - highEquityDate).days
        if currentDrawdownDays > longestDrawdown:
            longestDrawdown = currentDrawdownDays

    return DrawdownInfo(
        highEquityDate=highEquityDate,
        maxDrawdown=math.exp(maxDrawdown),
        longestDrawdown=longestDrawdown,
        currentDrawdown=math.exp(currentSum-maxSum),
        currentDrawdownDays=currentDrawdownDays,
    )


def printReport(r: HprStatistcs):
    print(f"Ежемесячная доходность {hprDisplay(r.monthHpr):.1f}%")
    print(
        f"Среднеквадратичное отклонение доходности за день {r.stDev*100:.1f}%")
    print(
        f"Средний убыток в день среди 5% худших дней {hprDisplay(r.aVaR):.1f}%")
    printDrawdownInfo(r.drawdownInfo)
    print("Доходности по дням")
    printHprs(r.dayHprs[-20:])
    print("Доходности по месяцам")
    printHprs(r.monthHprs)
    print("Доходности по годам")
    printHprs(r.yearHprs)


def printHprs(hprs: list[DateSum]):
    for item in hprs:
        print(
            f"{item.date.strftime(displayDateLayout)} {hprDisplay(item.sum):>8,.1f}%")


def printDrawdownInfo(data: DrawdownInfo):
    print(f"Максимальная просадка {hprDisplay(data.maxDrawdown):.1f}%")
    print(f"Продолжительная просадка {data.longestDrawdown} дн.")
    print(
        f"Текущая просадка {hprDisplay(data.currentDrawdown):.1f}% {data.currentDrawdownDays} дн.")
    print(
        f"Дата максимума эквити {data.highEquityDate.strftime(displayDateLayout)}")


def hprDisplay(hpr: float) -> float:
    return (hpr-1.0)*100.0


def lastDayOfMonth(d: datetime.date):
    _, days = calendar.monthrange(d.year, d.month)
    return datetime.date(d.year, d.month, days)


def lastDayOfYear(d: datetime.date):
    return datetime.date(d.year, 12, 31)
