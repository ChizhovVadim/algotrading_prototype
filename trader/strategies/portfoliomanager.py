import logging


class PortfolioManager:
    def __init__(self, broker):
        self._broker = broker
        self._portfolios = []

    def init(self):
        for portfolio in self._portfolios:
            limits = self._broker.getPortfolioLimits(portfolio)
            availableAmount = limits.startLimitOpenPos
            if portfolio.amountWeight is not None:
                availableAmount *= portfolio.amountWeight
            if portfolio.amountUpper is not None:
                availableAmount = min(availableAmount, portfolio.amountUpper)
            logging.info(
                f"Init portfolio {portfolio.clientKey} {portfolio.portfolio} {limits.startLimitOpenPos} {availableAmount}")
            portfolio.amountAvailable = availableAmount

    def checkStatus(self):
        print(f"{'Client':<10} {'Portfolio':<10} {'StartLimit':>10} {'Available':>10} {'VarMargin':>10} {'VarMargin':>10} {'Used':>10}")
        for portfolio in self._portfolios:
            limits = self._broker.getPortfolioLimits(portfolio)
            varMargin = limits.accVarMargin + limits.varMargin
            if limits.startLimitOpenPos:
                varMarginRatio = varMargin / limits.startLimitOpenPos
                usedRatio = limits.usedLimOpenPos / limits.startLimitOpenPos
            else:
                varMarginRatio = 0
                usedRatio = 0
            print(f"{portfolio.clientKey:<10} {portfolio.portfolio:<10} {limits.startLimitOpenPos:>10,.0f} {portfolio.amountAvailable:>10,.0f} {varMargin:>10,.0f} {varMarginRatio:>10,.2%} {usedRatio:>10,.2%}")
        print(f"Total portfolios: {len(self._portfolios)}")
