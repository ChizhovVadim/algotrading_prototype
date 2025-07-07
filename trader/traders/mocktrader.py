from domaintypes import PortfolioInfo, SecurityInfo, Order
import logging


class MockTrader:
    def __init__(self):
        self._positions = dict()

    def incomingAmount(self, portfolio: PortfolioInfo) -> float:
        return 1_000_000

    def _positionKey(self, portfolio: PortfolioInfo, security: SecurityInfo) -> str:
        return portfolio.portfolio+security.code

    def getPosition(self, portfolio: PortfolioInfo, security: SecurityInfo) -> float:
        return self._positions.get(self._positionKey(portfolio, security), 0)

    def registerOrder(self, order: Order):
        sPrice = _formatPrice(
            order.price, order.security.pricePrecision, order.security.priceStep)
        logging.info(f"registerOrder {order} {sPrice}")
        posKey = self._positionKey(order.portfolio, order.security)
        self._positions[posKey] = self._positions.get(posKey, 0) + order.volume

    def getLastCandles(self, security: SecurityInfo,
                       candleInterval: str):
        return []

    def subscribeCandles(self, security: SecurityInfo, candleInterval: str):
        pass


def _formatPrice(price: float, pricePrecision: int, priceStep: float) -> str:
    if priceStep:
        price = round(price / priceStep) * priceStep
    return f"{price:.{pricePrecision}f}"
