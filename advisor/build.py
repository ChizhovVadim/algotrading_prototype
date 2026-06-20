from .consttrend import ConstTrend
from .advisorvalidator import AdvisorValidator


class AdvisorBuilder:
    def __init__(self, name: str, settings = None):
        self._name = name
        if isinstance(settings, str):
            self._settings = parseSettings(settings)
        else:
            self._settings = settings

    def build(self):
        ind = self._create()
        if ind is None:
            raise ValueError("bad advisor name", self._name)
        return AdvisorValidator(ind)

    def _create(self):
        if self._name == "buyandhold":
            return ConstTrend.NewBuyAndHold()
        return None


def parseSettings(query_str: str):
    return dict(pair.split("=") for pair in query_str.split("_"))
