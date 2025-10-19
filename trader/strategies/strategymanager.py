
class StrategyManager:
    def __init__(self):
        self._strategies = []

    def init(self):
        for strategy in self._strategies:
            strategy.init()

    def checkStatus(self):
        for strategy in self._strategies:
            strategy.checkStatus()
        print(f"Total strategies: {len(self._strategies)}")

    def onSignal(self, signal):
        orderRegistered = False
        for strategy in self._strategies:
            if strategy.onSignal(signal):
                orderRegistered = True
        return orderRegistered
