
class ConstTrend:
    def NewBuyAndHold():
        return ConstTrend(1.0)

    def __init__(self, trend: float):
        self._trend = trend

    def add(self, dt, v):
        return True

    def value(self):
        return self._trend
