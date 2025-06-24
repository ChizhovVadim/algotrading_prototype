from domaintypes import Candle
from .domaintypes import Advice


def rndAdvisor(candle: Candle) -> Advice:
    return Advice(candle.SecurityCode, candle.DateTime, candle.ClosePrice, 1.0, None)
