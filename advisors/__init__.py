from .import sample
from .import validation
from .domaintypes import Advisor


def buildAdvisor(name: str):
    res = _makeAdvisor(name)
    if res is None:
        raise ValueError("bad advisor name", name)
    return validation.applyCandleValidation(res)


def _makeAdvisor(name: str):
    if name.startswith("sample_"):
        name = name.removeprefix("sample_")
        return sample.buildAdvisor(name)
    return None
