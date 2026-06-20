class AdvisorValidator:
    """
    - По дате выкидываем прошлые (потенциально повторяющиеся) бары.
    - Проверяем, что прогноз советника лежит в отрезке [-1, +1].
    - TODO Можно логировать большое изменение цены
    """
    def __init__(self, child):
        self._child = child
        self._prevTime = None

    def add(self, dt, v):
        if self._prevTime is not None and self._prevTime >= dt:
            return False
        self._prevTime = dt
        return self._child.add(dt, v)

    def value(self):
        pos = self._child.value()
        if not -1 <= pos <= 1:
            raise ValueError("bad position", pos)
        return pos
