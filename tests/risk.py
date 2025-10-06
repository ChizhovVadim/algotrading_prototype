import math
import statistics
import functools
from .domain import DateSum


def applyLever(hprs: list[DateSum], lever: float) -> list[DateSum]:
    return [DateSum(hpr.date, 1+lever*(hpr.sum-1)) for hpr in hprs]


def limitStdev(stdev: float):
    def f(hprs: list[DateSum]) -> bool:
        return statistics.stdev((math.log(x.sum) for x in hprs)) <= stdev
    return f


def optimalLever(hprs: list[DateSum], riskSpecification) -> float:
    minHpr = min(x.sum for x in hprs)
    if minHpr >= 1.0:
        # Просадок нет. Это невозможно.
        return 1.0
    maxLever = 1.0/(1.0-minHpr)
    bestHpr = 1.0
    bestLever = 0.0
    STEP = 0.1
    lever = STEP  # Шибко умные могли бы использовать метод деления отрезка пополам
    while lever <= maxLever:
        leverHprs = applyLever(hprs, lever)
        if riskSpecification and not riskSpecification(leverHprs):
            break
        hpr = functools.reduce(lambda x, y: x*y.sum, leverHprs, 1.0)
        if hpr < bestHpr:
            break
        bestHpr = hpr
        bestLever = lever
        lever += STEP
    return bestLever
