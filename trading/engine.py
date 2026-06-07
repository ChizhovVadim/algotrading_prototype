import queue

from historydata.model import Candle
from .signal import SignalService
from .strategy import StrategyService
from .monitoring import MonitoringService
from .model import CheckStatusUserCmd, ExitUserCmd


class Engine:
    def __init__(self, monitoring: MonitoringService):
        self._monitoring = monitoring
        self._inbox = queue.Queue()
        self._signals: list[SignalService] = []
        self._strategies: list[StrategyService] = []

    def send(self, msg):
        self._inbox.put(msg)

    def run(self):
        for signal in self._signals:
            signal.init()
        for strategy in self._strategies:
            strategy.init()
        self._checkStatus()
        # подписываемся как можно позже
        for signal in self._signals:
            signal.subscribe()

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
                self._checkStatus()

    def _onCandle(self, candle: Candle) -> bool:
        orderRegistered = False
        for signal in self._signals:
            s = signal._onCandle(candle)
            if s is None:
                continue
            for strategy in self._strategies:
                if strategy.onSignal(s):
                    orderRegistered = True
        return orderRegistered

    def _checkStatus(self):
        signals = [x.current() for x in self._signals]
        positions = [x.plannedPosition() for x in self._strategies]
        self._monitoring.update(signals, positions)
