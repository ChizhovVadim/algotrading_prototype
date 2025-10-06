

class WeightSum:
    """взвешенная сумма.
    сумма весов может быть больше 1. полезно для плавных индикаторов."""

    def __init__(self, childs, weights: list[float] = None):
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
