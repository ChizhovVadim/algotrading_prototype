from typing import NamedTuple, Protocol, Iterable
from dataclasses import dataclass
import datetime


class ExitUserCmd:
    pass


class CheckStatusUserCmd:
    pass


class Candle(NamedTuple):
    interval: str
    securityCode: str
    dateTime: datetime.datetime
    openPrice: float
    highPrice: float
    lowPrice: float
    closePrice: float
    volume: float


class Security(NamedTuple):
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


@dataclass
class Portfolio:
    clientKey: str
    "MultyBroker использует это поле для маршрутизации клиентов"
    firm: str
    portfolio: str
    amountWeight: float | None = None
    amountUpper: float | None = None
    amountAvailable: float | None = None


class Order(NamedTuple):
    portfolio: Portfolio
    security: Security
    volume: int
    price: float


class PortfolioLimits(NamedTuple):
    startLimitOpenPos: float
    "Лимит открытых позиций на начало дня"
    usedLimOpenPos: float
    "Текущие чистые позиции"
    varMargin: float
    "Вариац. маржа"
    accVarMargin: float
    "Накопленная вариационная маржа с учётом премии по опционам и биржевым сборам"


class MarketDataService(Protocol):
    def getLastCandles(self, security: Security, candleInterval: str) -> Iterable[Candle]:
        pass

    def subscribeCandles(self, security: Security, candleInterval: str):
        pass

    def lastPrice(self, security: Security) -> float:
        pass


class Broker(Protocol):
    def init(self):
        pass

    def checkStatus(self):
        pass

    def getPortfolioLimits(self, portfolio: Portfolio) -> PortfolioLimits:
        pass

    def getPosition(self, portfolio: Portfolio, security: Security) -> float:
        pass

    def registerOrder(self, order: Order):
        pass

    def close(self):
        pass
