import math
import statistics
import functools

from .datesum import DateSum


def applyLever(hprs: list[DateSum], lever: float) -> list[DateSum]:
    return [DateSum(hpr.Date, 1+lever*(hpr.Sum-1)) for hpr in hprs]


def limitStdev(stdev: float):
    def f(hprs: list[DateSum]) -> bool:
        nonlocal stdev
        return statistics.stdev((math.log(x.Sum) for x in hprs)) < stdev
    return f


def optimalLever(hprs: list[DateSum], riskSpecification) -> float:
    minHpr = min(x.Sum for x in hprs)
    if minHpr >= 1.0:
        # Просадок нет. Это невозможно.
        return 1.0
    maxLever = 1.0/(1.0-minHpr)
    bestHpr = 1.0
    bestLever = 0.0
    for ratio in range(1, 100):
        lever = maxLever*ratio/100.0
        leverHprs = applyLever(hprs, lever)
        if riskSpecification and not riskSpecification(leverHprs):
            break
        hpr = functools.reduce(lambda x, y: x*y.Sum, leverHprs, 1.0)
        if hpr < bestHpr:
            break
        bestHpr = hpr
        bestLever = lever
    return bestLever
