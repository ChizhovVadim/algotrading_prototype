import queue
import logging

from trader.domain import Candle, ExitUserCmd, CheckStatusUserCmd
from trader.brokers.multybroker import MultyBroker
from .signalmanager import SignalManager
from .strategymanager import StrategyManager
from .portfoliomanager import PortfolioManager


class Trader:
    def __init__(self):
        self._inbox = queue.Queue()
        self._broker = MultyBroker()
        self._signalManager = SignalManager()
        self._portfolioManager = PortfolioManager(self._broker)
        self._strategyManager = StrategyManager()
        self._shouldCheckStatus = False

    def close(self):
        self._broker.close()

    def checkStatus(self):
        self._broker.checkStatus()
        self._signalManager.checkStatus()
        self._portfolioManager.checkStatus()
        self._strategyManager.checkStatus()

    def onCandle(self, candle):
        signals = self._signalManager.onCandle(candle)
        for signal in signals:
            if self._strategyManager.onSignal(signal):
                self._shouldCheckStatus = True

    def run(self):
        self._broker.init()
        self._portfolioManager.init()
        self._strategyManager.init()
        self.checkStatus()
        logging.info("Strategies started.")
        # Подписываемся как можно позже перед чтением. Можно даже в отдельном потоке.
        self._signalManager.init()

        # находимся в главном потоке и здесь уже код потокобезопасный
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
            elif isinstance(message, ExitUserCmd):
                return
            elif isinstance(message, CheckStatusUserCmd):
                self.checkStatus()
