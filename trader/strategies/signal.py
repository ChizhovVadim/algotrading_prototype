import logging
import datetime
from typing import NamedTuple

from trader.brokers.domain import Candle, Security, MarketDataService


class SizeConfig(NamedTuple):
    longLever: float
    shortLever: float
    maxLever: float
    weight: float


class Signal(NamedTuple):
    name: str
    securityCode: str
    dateTime: datetime.datetime
    price: float
    prediction: float
    deadline: datetime.datetime | None
    contractsPerAmount: float | None


class SignalService:
    def __init__(self,
                 marketData: MarketDataService,
                 name: str,
                 ind,
                 security: Security,
                 candleInterval: str,
                 sizeConfig: SizeConfig):
        self._name = name
        self._marketData = marketData
        self._security = security
        self._candleInterval = candleInterval
        self._ind = ind
        self._sizeConfig = sizeConfig
        self._baseCandle: Candle | None = None
        self._lastSignal: Signal | None = None
        self._start = datetime.datetime.now() + datetime.timedelta(minutes=-10)

    def init(self):
        self.applyHistoryCandles(self._marketData.getLastCandles(
            self._security, self._candleInterval))
        logging.info(f"Init signal {self._lastSignal}")
        # Подписываться можно даже в отдельном потоке.
        self._marketData.subscribeCandles(self._security, self._candleInterval)

    def checkStatus(self):
        signal = self._lastSignal
        if signal is None:
            return
        status = {
            "Advisor": self._name,
            "Security": self._security.name,
            "DateTime": signal.dateTime.strftime("%d.%m.%Y %H:%M"),
            "Price": signal.price,
            "Prediction": signal.prediction,
        }
        print(status)

    def applyHistoryCandles(self, candles):
        size = 0
        first = None
        last = None
        for candle in candles:
            size += 1
            if first is None:
                first = candle
            last = candle

            if self._ind.add(candle.dateTime, candle.closePrice):
                self._lastSignal = Signal(
                    name=self._name,
                    securityCode=self._security.code,
                    dateTime=candle.dateTime,
                    price=candle.closePrice,
                    prediction=self._ind.value(),
                    contractsPerAmount=None,
                    deadline=None)

        if size == 0:
            logging.warning("History candles empty")
        else:
            logging.debug(f"History candles {size} {first} {last}")

    def onCandle(self, candle: Candle):
        # следим только за своими барами
        if not (candle.securityCode == self._security.code):
            # TODO and candle.interval == self._candleInterval):
            return None
        if not self._ind.add(candle.dateTime, candle.closePrice):
            return None

        freshCandle = candle.dateTime >= self._start

        if self._baseCandle is None and freshCandle:
            self._baseCandle = candle
            logging.debug(
                f"Init base price {self._baseCandle.dateTime} {self._baseCandle.closePrice}")

        prediction = self._ind.value()
        if not freshCandle:
            deadline = None
            contractsPerAmount = None
        else:
            deadline = candle.dateTime + datetime.timedelta(minutes=9)
            contractsPerAmount = applySizeConfig(
                prediction, self._sizeConfig) / (self._baseCandle.closePrice * self._security.lever)

        self._lastSignal = Signal(
            name=self._name,
            securityCode=self._security.code,
            dateTime=candle.dateTime,
            price=candle.closePrice,
            prediction=prediction,
            deadline=deadline,
            contractsPerAmount=contractsPerAmount,
        )

        if freshCandle:
            logging.debug(f"New signal {self._lastSignal}")
            return self._lastSignal
        else:
            return None


def applySizeConfig(pos: float, sizeConfig: SizeConfig) -> float:
    if pos > 0:
        pos *= sizeConfig.longLever
    else:
        pos *= sizeConfig.shortLever
    pos = max(-sizeConfig.maxLever, min(sizeConfig.maxLever, pos))
    pos *= sizeConfig.weight
    return pos
