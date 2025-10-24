from .domain import Broker, Portfolio, Security, Order, PortfolioLimits


class MultyBroker:
    def __init__(self):
        self._brokers = dict()

    def init(self):
        for broker in self._brokers.values():
            broker.init()

    def checkStatus(self):
        for broker in self._brokers.values():
            broker.checkStatus()
        print(f"Total brokers: {len(self._brokers)}")

    def get(self, clientKey: str):
        return self._brokers[clientKey]

    def add(self, clientKey: str, broker: Broker):
        self._brokers[clientKey] = broker

    def getPortfolioLimits(self, portfolio: Portfolio) -> PortfolioLimits:
        return self._brokers[portfolio.clientKey].getPortfolioLimits(portfolio)

    def getPosition(self, portfolio: Portfolio, security: Security) -> float:
        return self._brokers[portfolio.clientKey].getPosition(portfolio, security)

    def registerOrder(self, order: Order):
        return self._brokers[order.portfolio.clientKey].registerOrder(order)

    def close(self):
        for broker in self._brokers.values():
            broker.close()
