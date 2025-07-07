from domaintypes import Trader, PortfolioInfo, SecurityInfo, Order, SupportsClose


class MultyTrader:
    def __init__(self):
        self.__traders = dict()

    def get(self, clientKey: str):
        return self.__traders[clientKey]

    def add(self, trader: Trader, clientKey: str):
        self.__traders[clientKey] = trader

    def incomingAmount(self, portfolio: PortfolioInfo) -> float:
        return self.__traders[portfolio.clientKey].incomingAmount(portfolio)

    def getPosition(self, portfolio: PortfolioInfo, security: SecurityInfo) -> float:
        return self.__traders[portfolio.clientKey].getPosition(portfolio, security)

    def registerOrder(self, order: Order):
        return self.__traders[order.portfolio.clientKey].registerOrder(order)

    def close(self):
        for trader in self.__traders.values():
            if isinstance(trader, SupportsClose):
                trader.close()
