import queue
import threading

from domain.model.candle import Candle
from domain.trading.multybroker import MultyBroker
from domain.trading.monitoring import MonitoringService
from domain.trading.signal import SignalService
from domain.trading.strategy import StrategyService
from .usercommands import ExitUserCmd, CheckStatusUserCmd, readUserCommands


class TraderApp:
    def __init__(self):
        self._broker = MultyBroker()
        self._monitoring = MonitoringService(self._broker)
        self._signals: list[SignalService] = []
        self._strategies: list[StrategyService] = []
        self._inbox = queue.Queue()

    def close(self):
        self._broker.close()

    def checkStatus(self):
        signals = [x.current() for x in self._signals]
        positions = [x.plannedPosition() for x in self._strategies]
        self._monitoring.update(signals, positions)

    def subscribe(self):
        for signal in self._signals:
            signal.subscribe()

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

    def run(self):
        self._broker.init()
        for signal in self._signals:
            signal.init()
        for strategy in self._strategies:
            strategy.init()

        self.checkStatus()

        usercmd_thread = threading.Thread(target=readUserCommands, args=[self._inbox])
        usercmd_thread.start()

        # подписываемся как можно позже
        self.subscribe()

        # находимся в главном потоке и здесь уже код потокобезопасный
        shouldCheckStatus = False
        while True:
            timeout = 10.0 if shouldCheckStatus else None
            try:
                message = self._inbox.get(timeout=timeout)
            except queue.Empty:
                if shouldCheckStatus:
                    shouldCheckStatus = False
                    self.checkStatus()
                continue

            if isinstance(message, Candle):
                if self.onCandle(message):
                    shouldCheckStatus = True
            elif isinstance(message, ExitUserCmd):
                return
            elif isinstance(message, CheckStatusUserCmd):
                self.checkStatus()
