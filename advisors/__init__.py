"""Торговые советники"""

from . import indicators


class AdvisorBuilder:
    def __init__(self, name: str, stdVol: float):
        self._name = name or "main"
        self._stdVol = stdVol or 0.006

    def build(self):
        if self._name == "sample":
            return self.sample()

        raise ValueError("bad advisor name", self._name)

    def sample(self):
        volInd = indicators.Volatility(self._stdVol, 100)
        ind = indicators.WeightSum([
            indicators.BuyAndHold(),
        ])
        ind = indicators.EmaRebalance(volInd, ind, 1.0/25)
        ind = indicators.VolatilityWrapper(volInd, ind)
        ind = indicators.CandleValidator(ind)
        return ind
