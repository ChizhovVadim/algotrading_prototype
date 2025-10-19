
class SignalManager:
    def __init__(self):
        self._signals = []

    def init(self):
        for signal in self._signals:
            signal.init()

    def checkStatus(self):
        for signal in self._signals:
            signal.checkStatus()
        print(f"Total signals: {len(self._signals)}")

    def onCandle(self, candle):
        # TODO yield newSignal
        res = []
        for signal in self._signals:
            newSignal = signal.onCandle(candle)
            if newSignal is not None:
                res.append(newSignal)
        return res
