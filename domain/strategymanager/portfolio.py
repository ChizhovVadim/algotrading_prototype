import logging

from domain.model.broker import Portfolio, Broker


class PortfolioService:
    def __init__(self, broker: Broker, portfolio: Portfolio, amountWeight: float|None, amountUpper: float|None):
        self._broker = broker
        self._portfolio = portfolio
        self._amountWeight = amountWeight
        self._amountUpper = amountUpper
        self._amountAvailable : float | None = None

    def init(self):
        limits = self._broker.getPortfolioLimits(self._portfolio)
        availableAmount = limits.startLimitOpenPos
        if self._amountWeight is not None:
            availableAmount *= self._amountWeight
        if self._amountUpper is not None:
            availableAmount = min(availableAmount, self._amountUpper)
        logging.info(
            f"Init portfolio {self._portfolio.clientKey} {self._portfolio.portfolio} {limits.startLimitOpenPos} {availableAmount}")
        self._amountAvailable = availableAmount

    def getAmountAvailable(self):
        return self._amountAvailable

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
            "amountAvailable": self._amountAvailable,
            "varMargin": varMargin,
            "varMarginRatio": varMarginRatio,
            "usedRatio": usedRatio,
        }
        print(status)
