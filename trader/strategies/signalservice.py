import datetime
import logging
from typing import NamedTuple

import advisors
import domaintypes


class SignalConfig(NamedTuple):
    Advisor: str
    Security: str


def initSignal(
    securityInfoService: domaintypes.SecurityInfoService,
    marketDataService: domaintypes.MarketDataService,
    config: SignalConfig,
):
    security = securityInfoService.getSecurityInfo(config.Security)
    if security is None:
        raise ValueError("bad security", config.Security)
    candleInterval = domaintypes.CandleInterval.MINUTES5
    adv = advisors.buildAdvisor(config.Advisor)
    lastAdvice = None
    lastAdvice = applyHistoryCandles(
        adv, marketDataService.getLastCandles(security, candleInterval), lastAdvice)
    logging.info(f"Init advice {lastAdvice}")
    start = datetime.datetime.now()+datetime.timedelta(minutes=-10)
    return SignalService(config, security, candleInterval, adv, marketDataService, start)


def applyHistoryCandles(advisor, candles, lastAdvice):
    size = 0
    first = None
    last = None
    for candle in candles:
        size += 1
        if first is None:
            first = candle
        last = candle
        advice = advisor(candle)
        if advice is not None:
            lastAdvice = advice
    logging.info(f"History candles {size} {first} {last}")
    return lastAdvice


class SignalService:
    def __init__(self,
                 signalConfig: SignalConfig,
                 security: domaintypes.SecurityInfo,
                 candleInterval: str,
                 advisor: advisors.Advisor,
                 marketData: domaintypes.MarketDataService,
                 start: datetime.datetime):
        self._config = signalConfig
        self._security = security
        self._candleInterval = candleInterval
        self._advisor = advisor
        self._marketData = marketData
        self._start = start
        self._lastSignal = None

    def subscribe(self):
        self._marketData.subscribeCandles(self._security, self._candleInterval)

    def status(self):
        return self._lastSignal

    def onMarketData(self, candle: domaintypes.Candle):
        # следим только за своими барами
        if not (candle.SecurityCode == self._security.Code
                and candle.Interval == self._candleInterval):
            return None

        advice = self._advisor(candle)
        # считаем, что сигнал слишком старый
        if advice is None or advice.DateTime < self._start:
            return None

        self._lastSignal = domaintypes.Signal(
            Advisor=self._config.Advisor,
            Security=self._security,
            DateTime=candle.DateTime,
            Price=candle.ClosePrice,
            Position=advice.Position,
            Details=advice.Details)
        return self._lastSignal
