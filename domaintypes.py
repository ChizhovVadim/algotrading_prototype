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


class Signal(NamedTuple):
    advisor: str
    security: Security
    dateTime: datetime.datetime
    price: float
    position: float
    details: Any


class Portfolio(NamedTuple):
    clientKey: str
    "MultyTrader использует это поле для маршрутизации клиентов"
    firm: str
    portfolio: str
    amountWeight: float | None
    amountUpper: float | None


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


class SecurityInfoService(Protocol):
    def getSecurityInfo(self, securityName: str) -> Security:
        pass


class MarketDataService(Protocol):
    def getLastCandles(self, security: Security, candleInterval: str) -> Iterable[Candle]:
        pass

    def subscribeCandles(self, security: Security, candleInterval: str):
        pass

    def lastPrice(self, security: Security) -> float:
        pass


class Trader(Protocol):
    def getPortfolioLimits(self, portfolio: Portfolio) -> PortfolioLimits:
        pass

    def getPosition(self, portfolio: Portfolio, security: Security) -> float:
        pass

    def registerOrder(self, order: Order):
        pass


class SupportsClose(abc.ABC):
    @abc.abstractmethod
    def close(self):
        pass
