import logging
import datetime

from domain.model.candle import Candle
from domain.model.broker import Security, MarketDataService
from domain.model.trader import Signal


class SignalService:
    def __init__(
        self,
        marketData: MarketDataService,
        name: str,
        ind,
        security: Security,
        candleInterval: str,
    ):
        self._name = name
        self._marketData = marketData
        self._security = security
        self._candleInterval = candleInterval
        self._ind = ind
        self._start = datetime.datetime.now()
        self._currentSignal: Signal | None = None

    def init(self):
        self.applyHistoryCandles(
            self._marketData.getLastCandles(self._security, self._candleInterval)
        )
        logging.info(f"Init signal {self._currentSignal}")

    def subscribe(self):
        self._marketData.subscribeCandles(self._security, self._candleInterval)

    def current(self):
        return self._currentSignal

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
                self._currentSignal = Signal(
                    name=self._name,
                    deadline=candle.dateTime + datetime.timedelta(minutes=9),
                    price=candle.closePrice,
                    value=self._ind.value(),
                )

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

        self._currentSignal = Signal(
            name=self._name,
            deadline=candle.dateTime + datetime.timedelta(minutes=9),
            price=candle.closePrice,
            value=self._ind.value(),
        )
        if self._currentSignal.deadline < self._start:
            return None
        logging.debug(f"New signal {self._currentSignal}")
        return self._currentSignal
