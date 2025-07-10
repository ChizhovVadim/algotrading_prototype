import logging
import datetime
from typing import NamedTuple

import domaintypes


class StrategyConfig(NamedTuple):
    advisor: str
    security: str
    longLever: float
    shortLever: float
    maxLever: float
    weight: float


def initStrategy(
    securityInfoService: domaintypes.SecurityInfoService,
    trader: domaintypes.Trader,
    portfolio: domaintypes.Portfolio,
    config: StrategyConfig,
):
    security = securityInfoService.getSecurityInfo(config.security)
    if security is None:
        raise ValueError("bad security", config.security)

    return Strategy(config, trader, portfolio, security)


class Strategy:
    def __init__(self,
                 config: StrategyConfig,
                 trader: domaintypes.Trader,
                 portfolio: domaintypes.Portfolio,
                 security: domaintypes.Security,
                 ):

        self._config = config
        self._trader = trader
        self._portfolio = portfolio
        self._security = security
        self._amount = None
        self._position = None
        self._basePrice = None

    def initAmount(self, amount: float):
        self._amount = amount

    def initPos(self):
        self._position = self._trader.getPosition(
            self._portfolio, self._security)
        logging.info(
            f"Init position {self._portfolio.clientKey} {self._portfolio.portfolio} {self._security.name} {self._position}")

    def onSignal(self, signal: domaintypes.Signal) -> bool:
        # следим только за своими сигналами
        if not (self._security.code == signal.security.code and
                self._config.advisor == signal.advisor):
            return False

        # считаем, что сигнал слишком старый
        if signal.dateTime < datetime.datetime.now()-datetime.timedelta(minutes=9):
            return False

        if self._amount is None:
            logging.warning("strategy amount none")
            return False

        if self._position is None:
            logging.warning("strategy position none")
            return False

        position = self.computeDesiredPosition(signal)
        return self.rebalance(signal.price, position)

    def computeDesiredPosition(self, signal: domaintypes.Signal) -> float:
        if self._basePrice is None:
            self._basePrice = signal.price
            logging.debug(
                f"Init base price {self._security.name} {signal.dateTime} {self._basePrice}")
        if signal.position > 0:
            position = signal.position * self._config.longLever
        else:
            position = signal.position * self._config.shortLever
        position = self._config.weight * \
            max(-self._config.maxLever, min(self._config.maxLever, position))
        return position * self._amount / (self._basePrice * self._security.lever)

    def rebalance(self, price: float, desiredPosition: float) -> bool:
        volume = int(desiredPosition - self._position)
        # изменение позиции не требуется
        if volume == 0:
            return False

        traderPos = int(self._trader.getPosition(
            self._portfolio, self._security))
        if self._position != traderPos:
            logging.warning(
                f"Check position failed {self._position} {traderPos}")
            return False

        price = _priceWithSlippage(price, volume)
        self._trader.registerOrder(domaintypes.Order(
            portfolio=self._portfolio,
            security=self._security,
            volume=volume,
            price=price,
        ))
        self._position += volume
        return True

    def closeAll(self):
        pass

    def status(self):
        traderPos = int(self._trader.getPosition(
            self._portfolio, self._security))
        statusOk = traderPos == self._position
        return {
            "Client": self._portfolio.clientKey,
            "Portfolio": self._portfolio.portfolio,
            "Security": self._security.name,
            "StrategyPos": self._position,
            "TraderPos": traderPos,
            "Status": "+" if statusOk else "!",
        }


def _priceWithSlippage(price: float, volume: int) -> float:
    Slippage = 0.001
    if volume > 0:
        return price * (1 + Slippage)
    else:
        return price * (1 - Slippage)
