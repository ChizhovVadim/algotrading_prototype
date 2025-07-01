from typing import NamedTuple, Iterable, Any, Protocol
import abc
import datetime
import enum


class Candle(NamedTuple):
    Interval: str
    SecurityCode: str
    DateTime: datetime.datetime
    OpenPrice: float
    HighPrice: float
    LowPrice: float
    ClosePrice: float
    Volume: float


class CandleInterval(enum.StrEnum):
    MINUTES5 = "minutes5"
    HOURLY = "hourly"
    DAILY = "daily"


class SecurityInfo(NamedTuple):
    Name: str
    "Название инструмента"
    Code: str
    "Код инструмента"
    ClassCode: str
    "Код класса"
    PricePrecision: int
    "точность (кол-во знаков после запятой). Если шаг цены может быть не круглым (0.05), то этого будет недостаточно."
    PriceStep: float
    "шаг цены"
    PriceStepCost: float
    "Стоимость шага цены"
    Lever: float
    "Плечо. Для фьючерсов = PriceStepCost/PriceStep."


class Signal(NamedTuple):
    Advisor: str
    Security: SecurityInfo
    DateTime: datetime.datetime
    Price: float
    Position: float
    Details: Any


class PortfolioInfo(NamedTuple):
    ClientKey: str
    "MultyTrader использует это поле для маршрутизации клиентов"
    Firm: str
    Portfolio: str


class Order(NamedTuple):
    Portfolio: PortfolioInfo
    Security: SecurityInfo
    Volume: int
    Price: float


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
