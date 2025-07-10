import logging
from domaintypes import Portfolio, Security, Order, PortfolioLimits


class MockTrader:
    def __init__(self):
        self._positions = dict()

    def getPortfolioLimits(self, portfolio: Portfolio) -> PortfolioLimits:
        return PortfolioLimits(1_000_000., 0., 0., 0.)

    def _positionKey(self, portfolio: Portfolio, security: Security) -> str:
        return portfolio.portfolio+security.code

    def getPosition(self, portfolio: Portfolio, security: Security) -> float:
        return self._positions.get(self._positionKey(portfolio, security), 0)

    def registerOrder(self, order: Order):
        sPrice = _formatPrice(
            order.price, order.security.pricePrecision, order.security.priceStep)
        logging.info(f"registerOrder {order} {sPrice}")
        posKey = self._positionKey(order.portfolio, order.security)
        self._positions[posKey] = self._positions.get(posKey, 0) + order.volume

    def getLastCandles(self, security: Security,
                       candleInterval: str):
        return []

    def subscribeCandles(self, security: Security, candleInterval: str):
        pass


def _formatPrice(price: float, pricePrecision: int, priceStep: float) -> str:
    if priceStep:
        price = round(price / priceStep) * priceStep
    return f"{price:.{pricePrecision}f}"
