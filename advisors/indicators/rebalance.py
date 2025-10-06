import datetime


class FixedTimeRebalance:
    "Также в момент ребалансировки пересчитывает волатильность"

    def __init__(self, volInd, trendInd, periods: list[datetime.time]):
        self._volInd = volInd
        self._trendInd = trendInd
        self._periods = periods
        self._lastDate = None
        self._value = 0.0

    def add(self, dt, v):
        self._trendInd.add(dt, v)
        if isRebalace(self._lastDate, dt, self._periods):
            self._volInd.recalculate()
            volRatio = self._volInd.ratio()
            trend = self._trendInd.value()
            self._value = trend*volRatio

        self._lastDate = dt

    def value(self):
        return self._value


def isRebalace(
    prevTime: datetime.datetime,
    curTime: datetime.datetime,
    periods: list[datetime.time],
) -> bool:
    if prevTime is None:
        return False
    l = prevTime.time()
    r = curTime.time()
    for period in periods:
        if l < period <= r:
            return True
    return False


class EmaRebalance:
    def NewContRebalance(volInd, trendInd):
        return EmaRebalance(volInd, trendInd, 1.0)

    def __init__(self, volInd, trendInd, emaRatio: float):
        self._volInd = volInd
        self._trendInd = trendInd
        self._emaRatio = emaRatio
        self._value = 0.0

    def add(self, dt, v):
        self._volInd.recalculate()
        volRatio = self._volInd.ratio()
        self._trendInd.add(dt, v)
        trend = self._trendInd.value()
        value = volRatio*trend
        self._value += (value-self._value)*self._emaRatio

    def value(self):
        return self._value


class BoundRebalance:
    "trendInd возвращает 2 значения"

    def __init__(self, volInd, trendInd):
        self._volInd = volInd
        self._trendInd = trendInd
        self._value = 0.0

    def add(self, dt, v):
        self._volInd.recalculate()
        volRatio = self._volInd.ratio()
        self._trendInd.add(dt, v)
        lower, upper = self._trendInd.value()
        self._value = max(lower*volRatio, min(upper*volRatio, self._value))

    def value(self):
        return self._value
