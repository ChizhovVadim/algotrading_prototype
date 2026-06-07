from .buyandhold import BuyAndHold
from .candlevalidator import CandleValidator

class AdvisorBuilder:
    def __init__(self, name: str, stdVol: float):
        self._name = name or "main"
        self._stdVol = stdVol or 0.006

    def build(self):
        ind = self._create()
        if ind is None:
            raise ValueError("bad trend name", self._name)
        return CandleValidator(ind)

    def _create(self):
        if self._name == "buyandhold":
            return BuyAndHold()
        return None
