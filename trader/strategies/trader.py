import queue
import logging

from trader.brokers.multybroker import MultyBroker
from trader.brokers.domain import Candle
from trader import usercommands
from .signal import SignalService
from .strategy import StrategyService
from .portfolio import PortfolioService


class Trader:
    def __init__(self):
        self._inbox = queue.Queue()
        self._broker = MultyBroker()
        self._signals: list[SignalService] = []
        self._portfolios: list[PortfolioService] = []
        self._strategies: list[StrategyService] = []
        self._shouldCheckStatus = False

    def close(self):
        self._broker.close()

    def addStrategiesForAllSignalPortfolioPairs(self):
        for signal in self._signals:
            for portfolio in self._portfolios:
                self._strategies.append(StrategyService(
                    portfolio._broker, portfolio._portfolio, signal._security, signal._name))

    def init(self):
        logging.info("Strategies starting...")
        self._broker.init()
        for portfolio in self._portfolios:
            portfolio.init()
        for strategy in self._strategies:
            strategy.init()
        for signal in self._signals:
            signal.init()
        logging.info("Strategies started.")

    def checkStatus(self):
        self._broker.checkStatus()

        for signal in self._signals:
            signal.checkStatus()
        print(f"Total signals: {len(self._signals)}")

        for portfolio in self._portfolios:
            portfolio.checkStatus()
        print(f"Total portfolios: {len(self._portfolios)}")

        for strategy in self._strategies:
            strategy.checkStatus()
        print(f"Total strategies: {len(self._strategies)}")

    def onCandle(self, candle):
        for signal in self._signals:
            s = signal.onCandle(candle)
            if s is None:
                continue
            for strategy in self._strategies:
                if strategy.onSignal(s):
                    self._shouldCheckStatus = True

    def run(self):
        self.init()

        # находимся в главном потоке и здесь уже код потокобезопасный
        self._shouldCheckStatus = True
        while True:
            timeout = 10.0 if self._shouldCheckStatus else None
            try:
                message = self._inbox.get(timeout=timeout)
            except queue.Empty:
                if self._shouldCheckStatus:
                    self._shouldCheckStatus = False
                    self.checkStatus()
                continue

            if isinstance(message, Candle):
                self.onCandle(message)
            elif isinstance(message, usercommands.ExitUserCmd):
                return
            elif isinstance(message, usercommands.CheckStatusUserCmd):
                self.checkStatus()
