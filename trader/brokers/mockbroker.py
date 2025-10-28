import logging

from .domain import Portfolio, Security, Order, PortfolioLimits


class MockBroker:
    def __init__(self, name: str):
        self._name = name
        self._positions = dict()

    def init(self):
        logging.info(f"Init broker mock {self._name}")

    def checkStatus(self):
        pass

    def getPortfolioLimits(self, portfolio) -> PortfolioLimits:
        return PortfolioLimits(1_000_000, 0, 0, 0)

    def getPosition(self, portfolio: Portfolio, security: Security):
        return self._positions.get(_positionKey(portfolio, security), 0)

    def registerOrder(self, order: Order):
        logging.info(
            f"registerOrder {order.portfolio.clientKey} {order.portfolio.portfolio} {order.security.code} {order.price} {order.volume}")
        posKey = _positionKey(order.portfolio, order.security)
        self._positions[posKey] = self._positions.get(posKey, 0) + order.volume

    def getLastCandles(self, security, candleInterval):
        return []

    def subscribeCandles(self, security: Security, candleInterval):
        logging.debug(f"subscribeCandles {security.code} {candleInterval}")

    def close(self):
        pass


def _positionKey(portfolio: Portfolio, security: Security) -> str:
    return portfolio.portfolio+security.code
