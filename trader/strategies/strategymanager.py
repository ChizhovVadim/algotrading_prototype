import logging
import domaintypes
from .strategyservice import Strategy
from .signalservice import SignalService
from trader import usercommands


class StrategyManager:
    def __init__(self):
        self._signals = []
        self._strategies = []

    def addSignal(self, signal: SignalService):
        self._signals.append(signal)

    def addStrategy(self, strategy: Strategy):
        self._strategies.append(strategy)

    def subscribe(self):
        for signalService in self._signals:
            signalService.subscribe()

    def checkStatus(self):
        for signalService in self._signals:
            print(f"{signalService.status()}")

        for strategyService in self._strategies:
            print(f"{strategyService.status()}")

    def onMarketData(self, marketData):
        for signalService in self._signals:
            signal = signalService.onMarketData(marketData)
            if signal is None:
                continue
            for strategyService in self._strategies:
                try:
                    strategyService.onSignal(signal)
                except Exception as e:
                    logging.error(f"onSignal failed {e}")

    def initLimits(self):
        portfolioLimits = dict()
        for strategyService in self._strategies:
            portfolio = strategyService._portfolio
            amount = portfolioLimits.get(portfolio.Portfolio)
            if amount is None:
                amount = strategyService._trader.incomingAmount(portfolio)
                portfolioLimits[portfolio.Portfolio] = amount
                logging.info(
                    f"Init portfolio {portfolio.ClientKey} {portfolio.Portfolio} {amount}")
            strategyService.initAmount(amount)
            strategyService.initPos()

    def run(self, inbox):
        self.initLimits()
        self.subscribe()  # Подписываемся как можно позже перед чтением
        logging.info("Strategies started.")
        # находимся в главном потоке и здесь уже код потокобезопасный
        while True:
            message = inbox.get()  # можно с таймаутом, чтобы иногда вызывать checkStatus()
            if isinstance(message, domaintypes.Candle):
                self.onMarketData(message)
            elif isinstance(message, usercommands.ExitUserCmd):
                return
            elif isinstance(message, usercommands.CheckStatusUserCmd):
                self.checkStatus()
            elif isinstance(message, usercommands.InitLimitsUserCmd):
                self.initLimits()
