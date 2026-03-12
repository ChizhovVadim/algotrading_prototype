import queue
import threading

from domain.model.candle import Candle
from domain.strategymanager import StrategyManager
from .multybroker import MultyBroker
from .usercommands import ExitUserCmd, CheckStatusUserCmd, readUserCommands


class TraderApp:
    def __init__(self):
        self._broker = MultyBroker()
        self._strategyManager = StrategyManager()
        self._inbox = queue.Queue()

    def close(self):
        self._broker.close()

    def checkStatus(self):
        self._broker.checkStatus()
        self._strategyManager.checkStatus()

    def run(self):
        self._broker.init()
        self._strategyManager.init()
        self.checkStatus()

        usercmd_thread = threading.Thread(target=readUserCommands, args=[self._inbox])
        usercmd_thread.start()

        self._strategyManager.subscribe()  # Подписываться лучше в отдельном потоке. Тогда QuikBroker должен быть потокобезопасный.

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
                if self._strategyManager.onCandle(message):
                    shouldCheckStatus = True
            elif isinstance(message, ExitUserCmd):
                return
            elif isinstance(message, CheckStatusUserCmd):
                self.checkStatus()
