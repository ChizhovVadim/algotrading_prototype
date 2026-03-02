"""Торговые советники"""


class AdvisorBuilder:
    def __init__(self, name: str, stdVol: float):
        self._name = name or "main"
        self._stdVol = stdVol or 0.006

    def build(self):
        raise NotImplementedError()
