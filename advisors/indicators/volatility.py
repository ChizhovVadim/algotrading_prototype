import math
import collections
from .import dateutils, mathutils


class VolatilityWrapper:
    def __init__(self, volInd, trendInd):
        self._volInd = volInd
        self._trendInd = trendInd

    def add(self, dt, v):
        self._volInd.add(dt, v)
        self._trendInd.add(dt, v)

    def value(self):
        return self._trendInd.value()


class Volatility:

    def __init__(self, stdVol: float, period: int):
        self._stdVol = stdVol
        self._period = period
        self._increments = collections.deque(maxlen=period)
        self._prevTime = None
        self._prevPrice = None
        self._value = stdVol
        self._ratio = 1.0

    def add(self, dt, v: float):
        if self._prevTime is not None and dateutils.isOneDayMainSession(self._prevTime, dt):
            self._increments.append(math.log(v/self._prevPrice))
        self._prevTime = dt
        self._prevPrice = v

    def recalculate(self):
        if len(self._increments) < self._period:
            return
        self._value = mathutils.stDev(self._increments)*math.sqrt(len(self._increments))
        self._ratio = min(1.0, self._stdVol / self._value)

    def value(self) -> float:
        return self._value

    def ratio(self) -> float:
        return self._ratio
