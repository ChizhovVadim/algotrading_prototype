from typing import NamedTuple, Iterable, Any, Protocol
import abc
import datetime
import enum


class Candle(NamedTuple):
    interval: str
    securityCode: str
    dateTime: datetime.datetime
    openPrice: float
    highPrice: float
    lowPrice: float
    closePrice: float
    volume: float


class CandleInterval(enum.StrEnum):
    MINUTES5 = "minutes5"
    HOURLY = "hourly"
    DAILY = "daily"


class SecurityInfo(NamedTuple):
    name: str
    "Название инструмента"
    code: str
    "Код инструмента"
    classCode: str
    "Код класса"
    pricePrecision: int
    "точность (кол-во знаков после запятой). Если шаг цены может быть не круглым (0.05), то этого будет недостаточно."
    priceStep: float
    "шаг цены"
    priceStepCost: float
    "Стоимость шага цены"
    lever: float
    "Плечо. Для фьючерсов = PriceStepCost/PriceStep."


class Signal(NamedTuple):
    advisor: str
    security: SecurityInfo
    dateTime: datetime.datetime
    price: float
    position: float
    details: Any


class PortfolioInfo(NamedTuple):
    clientKey: str
    "MultyTrader использует это поле для маршрутизации клиентов"
    firm: str
    portfolio: str


class Order(NamedTuple):
    portfolio: PortfolioInfo
    security: SecurityInfo
    volume: int
    price: float


class SecurityInfoService(Protocol):
    def getSecurityInfo(self, securityName: str) -> SecurityInfo:
        pass


class MarketDataService(Protocol):
    def getLastCandles(self, security: SecurityInfo, candleInterval: str) -> Iterable[Candle]:
        pass

    def subscribeCandles(self, security: SecurityInfo, candleInterval: str):
        pass


class Trader(Protocol):
    def incomingAmount(self, portfolio: PortfolioInfo) -> float:
        pass

    def getPosition(self, portfolio: PortfolioInfo, security: SecurityInfo) -> float:
        pass

    def registerOrder(self, order: Order):
        pass


class SupportsClose(abc.ABC):
    @abc.abstractmethod
    def close(self):
        pass
