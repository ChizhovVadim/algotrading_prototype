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
        print(f"Signal size: {len(self._signals)}")
        for signalService in self._signals:
            print(f"{signalService.status()}")

        portfolios = dict()
        for strategyService in self._strategies:
            portfolio = strategyService._portfolio
            if portfolio.portfolio in portfolios:
                continue
            limits = strategyService._trader.getPortfolioLimits(portfolio)
            portfolios[portfolio.portfolio] = {
                "Client": portfolio.clientKey,
                "Portfolio": portfolio.portfolio,
                "StartLimitOpenPos": limits.startLimitOpenPos,
                "AccVarMargin": limits.accVarMargin,
                "VarMargin": limits.varMargin,
                "UsedLimOpenPos": limits.usedLimOpenPos,
            }

        print(f"Portfolio size: {len(portfolios)}")
        # TODO Печать в виде таблицы
        for portfolioStatus in portfolios.values():
            print(portfolioStatus)

        print(f"Strategy size: {len(self._strategies)}")
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

    def closeAll(self):
        # TODO нужно перестать получать сигналы, (чтобы не открыть позицию заново)
        for strategyService in self._strategies:
            strategyService.closeAll()

    def initLimits(self):
        portfolioLimits = dict()
        for strategyService in self._strategies:
            portfolio = strategyService._portfolio
            amount = portfolioLimits.get(portfolio.portfolio)
            if amount is None:
                amount = self.calcLimit(strategyService._trader, portfolio)
                portfolioLimits[portfolio.portfolio] = amount
            strategyService.initAmount(amount)
            strategyService.initPos()

    def calcLimit(self, trader: domaintypes.Trader, portfolio: domaintypes.Portfolio) -> float:
        limits = trader.getPortfolioLimits(portfolio)
        availableAmount = limits.startLimitOpenPos
        if portfolio.amountWeight is not None:
            availableAmount *= portfolio.amountWeight
        if portfolio.amountUpper is not None:
            availableAmount = min(availableAmount, portfolio.amountUpper)
        logging.info(
            f"Init portfolio {portfolio.clientKey} {portfolio.portfolio} {availableAmount}")
        return availableAmount

    def run(self, inbox):
        self.initLimits()
        self.checkStatus()
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
            elif isinstance(message, usercommands.CloseAllUserCmd):
                self.closeAll()
