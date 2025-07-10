from domaintypes import Trader, Portfolio, Security, Order, PortfolioLimits, SupportsClose


class MultyTrader:
    def __init__(self):
        self.__traders = dict()

    def get(self, clientKey: str):
        return self.__traders[clientKey]

    def add(self, trader: Trader, clientKey: str):
        self.__traders[clientKey] = trader

    def getPortfolioLimits(self, portfolio: Portfolio) -> PortfolioLimits:
        return self.__traders[portfolio.clientKey].getPortfolioLimits(portfolio)

    def getPosition(self, portfolio: Portfolio, security: Security) -> float:
        return self.__traders[portfolio.clientKey].getPosition(portfolio, security)

    def registerOrder(self, order: Order):
        return self.__traders[order.portfolio.clientKey].registerOrder(order)

    def close(self):
        for trader in self.__traders.values():
            if isinstance(trader, SupportsClose):
                trader.close()
