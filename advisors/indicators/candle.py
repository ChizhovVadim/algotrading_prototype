

class CandleValidator:
    def __init__(self, trendInd):
        self._trendInd = trendInd
        self._prevTime = None

    def add(self, dt, v):
        if self._prevTime is not None and self._prevTime >= dt:
            return False
        self._trendInd.add(dt, v)
        self._prevTime = dt
        return True

    def value(self):
        return self._trendInd.value()
