import queue
import logging

from .brokers.domain import Candle
from .import usercommands
from .brokers.multybroker import MultyBroker
from .strategies.signalmanager import SignalManager
from .strategies.strategymanager import StrategyManager
from .strategies.portfoliomanager import PortfolioManager


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
        logging.info("Strategies starting...")
        self._broker.init()
        self._portfolioManager.init()
        self._strategyManager.init()
        self._signalManager.init()
        logging.info("Strategies started.")

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
