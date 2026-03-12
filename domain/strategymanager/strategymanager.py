import logging

from domain.model.candle import Candle
from .signal import SignalService
from .strategy import StrategyService
from .portfolio import PortfolioService


class StrategyManager:
    def __init__(self):
        self._signals: list[SignalService] = []
        self._portfolios: list[PortfolioService] = []
        self._strategies: list[StrategyService] = []

    def addStrategiesForAllSignalPortfolioPairs(self):
        for signal in self._signals:
            for portfolio in self._portfolios:
                self._strategies.append(StrategyService(signal, portfolio))

    def init(self):
        logging.info("Strategies starting...")
        for portfolio in self._portfolios:
            portfolio.init()
        for strategy in self._strategies:
            strategy.init()
        for signal in self._signals:
            signal.init()
        logging.info("Strategies started.")

    def subscribe(self):
        for signal in self._signals:
            signal.subscribe()

    def checkStatus(self):
        for signal in self._signals:
            signal.checkStatus()
        print(f"Total signals: {len(self._signals)}")

        for portfolio in self._portfolios:
            portfolio.checkStatus()
        print(f"Total portfolios: {len(self._portfolios)}")

        for strategy in self._strategies:
            strategy.checkStatus()
        print(f"Total strategies: {len(self._strategies)}")

    def onCandle(self, candle: Candle) -> bool:
        orderRegistered = False
        for signal in self._signals:
            s = signal.onCandle(candle)
            if s is None:
                continue
            for strategy in self._strategies:
                if strategy.onSignal(s):
                    orderRegistered = True
        return orderRegistered
