
class Direction:
    def LongOnly(child):
        return Direction(child, 1, 0)

    def __init__(self, child, longRatio: float, shortRatio: float):
        self._child = child
        self._longRatio = longRatio
        self._shortRatio = shortRatio

    def add(self, dt, v):
        self._child.add(dt, v)

    def value(self):
        res = self._child.value()
        if res > 0:
            res *= self._longRatio
        else:
            res *= self._shortRatio
        return res
