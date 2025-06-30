from .import sample
from .domaintypes import Advisor


def buildAdvisor(name: str):
    if name.startswith("sample_"):
        name = name.removeprefix("sample_")
        return sample.buildAdvisor(name)
    return None
