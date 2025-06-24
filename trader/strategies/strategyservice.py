import logging
import datetime
from typing import NamedTuple

import domaintypes


class StrategyConfig(NamedTuple):
    Advisor: str
    Security: str
    LongLever: float
    ShortLever: float
    MaxLever: float
    Weight: float


def initStrategy(
    securityInfoService: domaintypes.SecurityInfoService,
    trader: domaintypes.Trader,
    portfolio: domaintypes.PortfolioInfo,
    config: StrategyConfig,
):
    security = securityInfoService.getSecurityInfo(config.Security)
    if security is None:
        raise ValueError("bad security", config.Security)

    return Strategy(config, trader, portfolio, security)


class Strategy:
    def __init__(self,
                 config: StrategyConfig,
                 trader: domaintypes.Trader,
                 portfolio: domaintypes.PortfolioInfo,
                 security: domaintypes.SecurityInfo,
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
            f"Init position {self._portfolio.ClientKey} {self._portfolio.Portfolio} {self._security.Name} {self._position}")

    def onSignal(self, signal: domaintypes.Signal)-> bool:
        # следим только за своими сигналами
        if not (self._security.Code == signal.Security.Code and
                self._advisor == signal.Advisor):
            return False

        # считаем, что сигнал слишком старый
        if signal.DateTime < datetime.datetime.now()-datetime.timedelta(minutes=9):
            return False

        if self._amount is None:
            logging.warning("strategy amount none")
            return False

        if self._position is None:
            logging.warning("strategy position none")
            return False

        position = self.computeDesiredPosition(signal)
        return self.rebalance(signal.Price, position)

    def computeDesiredPosition(self, signal: domaintypes.Signal) -> float:
        if self._basePrice is None:
            self._basePrice = signal.Price
            logging.debug(
                f"Init base price {self._security.Name} {signal.DateTime} {self._basePrice}")
        if signal.Position > 0:
            position = signal.Position * self._config.LongLever
        else:
            position = signal.Position * self._config.ShortLever
        position = self._config.Weight * \
            max(-self._config.MaxLever, min(self._config.MaxLever, position))
        return position * self._amount / (self._basePrice * self._security.Lever)

    def rebalance(self, price: float, desiredPosition: float) -> bool:
        volume = int(desiredPosition - self._position)
        # изменение позиции не требуется
        if volume == 0:
            return False

        traderPos = int(self._trader.getPosition(
            self._portfolio, self._security))
        if self._position != traderPos:
            logging.warning(f"Check position {self._position} {traderPos} !")
            return False

        price = _priceWithSlippage(price, volume)
        self._trader.registerOrder(domaintypes.Order(
            Portfolio=self._portfolio,
            Security=self._security,
            Volume=volume,
            Price=price,
        ))
        self._position += volume
        return True

    def status(self):
        traderPos = int(self._trader.getPosition(
            self._portfolio, self._security))
        statusOk = traderPos == self._position
        return {
            "Client": self._portfolio.ClientKey,
            "Portfolio": self._portfolio.Portfolio,
            "Security": self._security.Name,
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
