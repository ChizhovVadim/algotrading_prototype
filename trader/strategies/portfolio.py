import logging

from trader.brokers.domain import Broker
from .domain import Portfolio


class PortfolioService:
    def __init__(self, broker: Broker, portfolio: Portfolio):
        self._broker = broker
        self._portfolio = portfolio

    def init(self):
        limits = self._broker.getPortfolioLimits(self._portfolio)
        availableAmount = limits.startLimitOpenPos
        if self._portfolio.amountWeight is not None:
            availableAmount *= self._portfolio.amountWeight
        if self._portfolio.amountUpper is not None:
            availableAmount = min(availableAmount, self._portfolio.amountUpper)
        logging.info(
            f"Init portfolio {self._portfolio.clientKey} {self._portfolio.portfolio} {limits.startLimitOpenPos} {availableAmount}")
        self._portfolio.amountAvailable = availableAmount

    def checkStatus(self):
        limits = self._broker.getPortfolioLimits(self._portfolio)
        varMargin = limits.accVarMargin + limits.varMargin
        if limits.startLimitOpenPos:
            varMarginRatio = varMargin / limits.startLimitOpenPos
            usedRatio = limits.usedLimOpenPos / limits.startLimitOpenPos
        else:
            varMarginRatio = 0
            usedRatio = 0
        #print(f"{self._portfolio.clientKey:<10} {self._portfolio.portfolio:<10} {limits.startLimitOpenPos:>10,.0f} {self._portfolio.amountAvailable:>10,.0f} {varMargin:>10,.0f} {varMarginRatio:>10,.2%} {usedRatio:>10,.2%}")
        status = {
            "Client": self._portfolio.clientKey,
            "Portfolio": self._portfolio.portfolio,
            "startLimitOpenPos": limits.startLimitOpenPos,
            "amountAvailable": self._portfolio.amountAvailable,
            "varMargin": varMargin,
            "varMarginRatio": varMarginRatio,
            "usedRatio": usedRatio,
        }
        print(status)
