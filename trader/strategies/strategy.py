import datetime
import logging

from trader.brokers.domain import Broker, Security, Order
from .domain import Portfolio
from .signal import Signal


class StrategyService:
    def __init__(self, broker: Broker, portfolio: Portfolio, security: Security, signalName: str):
        self._broker = broker
        self._portfolio = portfolio
        self._security = security
        self._signalName = signalName
        self._plannedPosition: int | None = None

    def brokerPosition(self):
        return int(self._broker.getPosition(self._portfolio, self._security))

    def init(self):
        self._plannedPosition = self.brokerPosition()
        logging.info(
            f"Init strategy {self._portfolio.clientKey} {self._portfolio.portfolio} {self._security.name} {self._plannedPosition}")

    def checkStatus(self):
        try:
            actualPosition = self.brokerPosition()
        except Exception:
            actualPosition = None
        status = {
            "Client": self._portfolio.clientKey,
            "Portfolio": self._portfolio.portfolio,
            "Security": self._security.name,
            "PlannedPos": self._plannedPosition,
            "ActualPos": actualPosition,
            "Status": "+" if self._plannedPosition == actualPosition else "!",
        }
        print(status)

    def onSignal(self, signal: Signal):
        # следим только за своими сигналами
        if not (self._security.code == signal.securityCode and
                self._signalName == signal.name):
            return False

        # считаем, что сигнал слишком старый
        if signal.deadline is not None and signal.deadline < datetime.datetime.now():
            return False

        if signal.contractsPerAmount is None:
            return False

        if self._portfolio.amountAvailable is None:
            return False

        idealPos = signal.contractsPerAmount * self._portfolio.amountAvailable
        return self.rebalance(signal.price, idealPos)

    def rebalance(self, price: float, idealPos: float):
        if self._plannedPosition is None:
            return False

        volume = int(idealPos - self._plannedPosition)
        if volume == 0:
            # изменение позиции не требуется
            return False

        try:
            brokerPos = self.brokerPosition()
        except Exception:
            return False
        if brokerPos != self._plannedPosition:
            logging.warning(
                f"check position failed {self._plannedPosition} {brokerPos}")
            return False

        price = _priceWithSlippage(price, volume)
        try:
            self._broker.registerOrder(Order(
                portfolio=self._portfolio,
                security=self._security,
                volume=volume,
                price=price,
            ))
        except Exception:
            logging.exception("broker.registerOrder")

        self._plannedPosition += volume
        return True


def _priceWithSlippage(price: float, volume: int) -> float:
    Slippage = 0.001
    if volume > 0:
        return price * (1 + Slippage)
    else:
        return price * (1 - Slippage)
