import datetime
import logging
from typing import NamedTuple

import advisors
import domaintypes


class SignalConfig(NamedTuple):
    advisor: str
    security: str


def initSignal(
    securityInfoService: domaintypes.SecurityInfoService,
    marketDataService: domaintypes.MarketDataService,
    candleStorage,
    config: SignalConfig,
):
    security = securityInfoService.getSecurityInfo(config.security)
    if security is None:
        raise ValueError("bad security", config.security)
    candleInterval = domaintypes.CandleInterval.MINUTES5
    adv = advisors.buildAdvisor(config.advisor)
    lastAdvice = None
    if candleStorage is not None:
        lastAdvice = applyHistoryCandles(
            adv, candleStorage.read(security.name), lastAdvice)
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

    def onMarketData(self, candle: domaintypes.Candle) -> domaintypes.Signal | None:
        # следим только за своими барами
        if not (candle.securityCode == self._security.code
                and candle.interval == self._candleInterval):
            return None

        advice = self._advisor(candle)
        # считаем, что сигнал слишком старый
        if advice is None or advice.dateTime < self._start:
            return None

        signal = domaintypes.Signal(
            advisor=self._config.advisor,
            security=self._security,
            dateTime=candle.dateTime,
            price=candle.closePrice,
            position=advice.position,
            details=advice.details)

        logging.debug(f"New signal {signal}")

        self._lastSignal = signal
        return signal
