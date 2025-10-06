from .daycandle import DayCandleAccumulator


class BuyAndHold:
    def __init__(self):
        pass

    def add(self, dt, v):
        pass

    def value(self):
        return 1.0


class Turtle:
    def __init__(self, period: int):
        self._period = period
        self._acc = DayCandleAccumulator()
        self._value = 0.0

    def add(self, dt, v):
        self._acc.add(dt, v)

    def value(self):
        dayCandles = self._acc._dayCandles
        lastPrice = dayCandles[-1].closePrice
        high = None
        low = None
        for i in range(1, self._period):
            if i >= len(dayCandles):
                break
            item = dayCandles[len(dayCandles)-1-i]
            if high is None:
                high = item.highPrice
                low = item.lowPrice
            else:
                high = max(high, item.highPrice)
                low = min(low, item.lowPrice)

        if high is not None:
            if lastPrice >= high:
                self._value = 1.0
            elif lastPrice <= low:
                self._value = -1.0
        return self._value
