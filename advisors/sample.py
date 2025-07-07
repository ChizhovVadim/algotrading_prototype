import datetime
from domaintypes import Candle
from .domaintypes import Advice


def buildAdvisor(name: str):
    if name == "momentum":
        return momentumAdvisor()
    return None


def momentumAdvisor():
    ind = WeightSumIndicator(
        [MomentumIndicator(1),
         MomentumIndicator(2),
         MomentumIndicator(5),
         MomentumIndicator(10),
         MomentumIndicator(20)],
        [0.2, 0.2, 0.2, 0.2, 0.2])
    ind = EmaIndicator(1.0/25, ind)
    ind = CandleDecorator(ind)
    return advisorFromIndicator(ind)


def advisorFromIndicator(trendIndicator):
    position = 0.0

    def f(c: Candle) -> Advice:
        nonlocal position
        trendIndicator.add(c.dateTime, c.closePrice)
        trend = trendIndicator.value()
        if trend is not None:
            position = trend
        return Advice(c.securityCode, c.dateTime, c.closePrice, position, None)
    return f


class EmaIndicator:
    def __init__(self, ratio: float, child):
        self._ratio = ratio
        self._child = child
        self._value = None

    def add(self, dt, v):
        self._child.add(dt, v)
        childValue = self._child.value()
        if childValue is None:
            return
        if self._value is None:
            self._value = childValue
        else:
            self._value = (1.0-self._ratio)*self._value + \
                self._ratio*childValue

    def value(self):
        return self._value


class WeightSumIndicator:
    def __init__(self, childs, weights: list[float]):
        if weights is None:
            weights = [1.0/len(childs) for _ in childs]
        elif len(childs) != len(weights):
            raise ValueError("wrong size WeightSumIndicator")
        self._childs = childs
        self._weights = weights
        self._values = [0.0 for _ in childs]

    def add(self, dt, v):
        for child in self._childs:
            child.add(dt, v)

    def value(self):
        hasValue = False
        for i, child in enumerate(self._childs):
            childValue = child.value()
            if childValue is not None:
                hasValue = True
                self._values[i] = childValue
        if not hasValue:
            return None
        sum = 0.0
        for w, v in zip(self._weights, self._values):
            sum += w * v
        return max(-1, min(1, sum))


def compare(l, r: float) -> float:
    if r > l:
        return 1.0
    if r < l:
        return -1.0
    return 0.0


class MomentumIndicator:
    def __init__(self, dayPeriod):
        self._period = dayPeriod
        self._candles = []
        self._lastDate = None
        self._lastPrice = None

    def add(self, dt, v):
        curDate = dt.date()
        if self._lastDate != curDate:
            self._candles.append(v)
            self._lastDate = curDate
        self._lastPrice = v

    def value(self):
        if len(self._candles) <= self._period:
            return None
        return compare(self._candles[-1-self._period], self._lastPrice)


class CandleDecorator:
    def __init__(self, trendIndicator):
        self._trendIndicator = trendIndicator

    def add(self, dt, v: float):
        if isMainFortsSession(dt):
            self._trendIndicator.add(dt, v)

    def value(self) -> float:
        return self._trendIndicator.value()


def isMainFortsSession(d: datetime.datetime) -> bool:
    return d.hour >= 10 and d.hour <= 18
