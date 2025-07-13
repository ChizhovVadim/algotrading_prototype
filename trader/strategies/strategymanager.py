import logging
import queue

import domaintypes
from .strategyservice import Strategy
from .signalservice import SignalService
from trader import usercommands


class StrategyManager:
    def __init__(self):
        self._signals = []
        self._strategies = []
        self._shouldCheckStatus = False

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
        print(f"Total signals: {len(self._signals)}")

        print(f"{'Client':<10} {'Portfolio':<10} {'StartLimit':>10} {'Available':>10} {'Acc':>10} {'VarMargin':>10} {'Used':>10}")
        visitedPortfolios = set()
        for strategyService in self._strategies:
            portfolio = strategyService._portfolio
            if portfolio.portfolio in visitedPortfolios:
                continue
            visitedPortfolios.add(portfolio.portfolio)
            limits = strategyService._trader.getPortfolioLimits(portfolio)
            print(f"{portfolio.clientKey:<10} {portfolio.portfolio:<10} {limits.startLimitOpenPos:>10,.0f} {portfolio.amountAvailable:>10,.0f} {limits.accVarMargin:>10,.0f} {limits.varMargin:>10,.0f} {limits.usedLimOpenPos:>10,.0f}")
        print(f"Total portfolios: {len(visitedPortfolios)}")

        for strategyService in self._strategies:
            print(f"{strategyService.status()}")
        print(f"Total strategies: {len(self._strategies)}")

    def onMarketData(self, marketData):
        for signalService in self._signals:
            signal = signalService.onMarketData(marketData)
            if signal is None:
                continue
            for strategyService in self._strategies:
                try:
                    if strategyService.onSignal(signal):
                        self._shouldCheckStatus = True
                except Exception:
                    logging.exception("onSignal failed")

    def closeAll(self):
        # TODO нужно перестать получать сигналы, (чтобы не открыть позицию заново)
        for strategyService in self._strategies:
            strategyService.closeAll()

    def initLimits(self):
        self.initPortfolioLimits()
        self.initStrategyPositions()

    def initPortfolioLimits(self):
        visitedPortfolios = set()
        for strategyService in self._strategies:
            portfolio = strategyService._portfolio
            if portfolio.portfolio not in visitedPortfolios:
                self.initPortfolioLimit(strategyService._trader, portfolio)
                visitedPortfolios.add(portfolio.portfolio)

    def initPortfolioLimit(self, trader: domaintypes.Trader, portfolio: domaintypes.Portfolio):
        limits = trader.getPortfolioLimits(portfolio)
        availableAmount = limits.startLimitOpenPos
        if portfolio.amountWeight is not None:
            availableAmount *= portfolio.amountWeight
        if portfolio.amountUpper is not None:
            availableAmount = min(availableAmount, portfolio.amountUpper)
        logging.info(
            f"Init portfolio {portfolio.clientKey} {portfolio.portfolio} {limits.startLimitOpenPos} {availableAmount}")
        portfolio.amountAvailable = availableAmount

    def initStrategyPositions(self):
        for strategyService in self._strategies:
            strategyService.initPos()

    def run(self, inbox: queue.Queue):
        self.initLimits()
        self.subscribe()  # Подписываемся как можно позже перед чтением
        logging.info("Strategies started.")
        self._shouldCheckStatus = True
        # находимся в главном потоке и здесь уже код потокобезопасный
        while True:
            try:
                timeout = 10.0 if self._shouldCheckStatus else None
                message = inbox.get(timeout=timeout)
            except queue.Empty:
                if self._shouldCheckStatus:
                    self._shouldCheckStatus = False
                    self.checkStatus()
                continue

            if isinstance(message, domaintypes.Candle):
                self.onMarketData(message)
            elif isinstance(message, usercommands.ExitUserCmd):
                return
            elif isinstance(message, usercommands.CheckStatusUserCmd):
                self.checkStatus()
            elif isinstance(message, usercommands.InitLimitsUserCmd):
                self.initLimits()
            elif isinstance(message, usercommands.CloseAllUserCmd):
                self.closeAll()
