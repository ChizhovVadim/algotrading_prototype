class CandleValidator:
    def __init__(self, trendInd):
        self._trendInd = trendInd
        self._prevTime = None

    def add(self, dt, v):
        if self._prevTime is not None and self._prevTime >= dt:
            return False
        self._prevTime = dt
        return self._trendInd.add(dt, v)

    def value(self):
        return self._trendInd.value()
