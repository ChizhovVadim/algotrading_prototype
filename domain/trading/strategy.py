import datetime
import logging
from typing import NamedTuple

from domain.model.broker import Broker, Security, Order, Portfolio
from domain.model.trader import Signal, PlannedPosition


class SizePolicy(NamedTuple):
    longLever: float
    shortLever: float
    maxLever: float
    weight: float


class StrategyService:
    def __init__(
        self,
        broker: Broker,
        portfolio: Portfolio,
        security: Security,
        signalName: str,
        sizePolicy: SizePolicy,
    ):
        self._broker = broker
        self._portfolio = portfolio
        self._security = security
        self._signalName = signalName
        self._sizePolicy = sizePolicy
        self._amountAvailable: float | None = None
        self._plannedPosition: int | None = None
        self._basePrice: Signal | None = None

    def brokerPosition(self):
        return int(self._broker.getPosition(self._portfolio, self._security))

    def init(self):
        self._plannedPosition = self.brokerPosition()
        limits = self._broker.getPortfolioLimits(self._portfolio)
        self._amountAvailable = limits.startLimitOpenPos

        logging.info(
            f"Init strategy {self._portfolio.clientKey} {self._portfolio.portfolio} {self._security.name} {self._plannedPosition} {self._amountAvailable}"
        )

    def plannedPosition(self):
        return PlannedPosition(self._portfolio, self._security, self._plannedPosition)

    def onSignal(self, signal: Signal):
        # следим только за своими сигналами
        if not (self._signalName == signal.name):
            return False

        # считаем, что сигнал слишком старый
        if signal.deadline < datetime.datetime.now():
            return False

        if self._basePrice is None:
            self._basePrice = signal
            logging.debug(f"Init base price {self._basePrice}")

        idealPos = calcIdealPos(
            self._amountAvailable,
            signal.value,
            self._sizePolicy,
            self._security,
            self._basePrice.price,
        )
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
                f"check position failed {self._plannedPosition} {brokerPos}"
            )
            return False

        price = _priceWithSlippage(signal.price, volume)
        try:
            self._broker.registerOrder(
                Order(
                    portfolio=self._portfolio,
                    security=self._security,
                    volume=volume,
                    price=price,
                )
            )
        except Exception:
            logging.exception("broker.registerOrder")

        self._plannedPosition += volume
        return True


def calcIdealPos(
    amount: float,
    prediction: float,
    sizePolicy: SizePolicy,
    security: Security,
    price: float,
) -> float:
    pos = prediction
    if pos > 0:
        pos *= sizePolicy.longLever
    else:
        pos *= sizePolicy.shortLever
    pos = max(-sizePolicy.maxLever, min(sizePolicy.maxLever, pos))
    return amount * sizePolicy.weight * pos / (price * security.lever)


def _priceWithSlippage(price: float, volume: int) -> float:
    Slippage = 0.001
    if volume > 0:
        return price * (1 + Slippage)
    else:
        return price * (1 - Slippage)
