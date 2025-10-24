from dataclasses import dataclass
import trader.brokers.domain


@dataclass
class Portfolio(trader.brokers.domain.Portfolio):
    amountWeight: float | None = None
    amountUpper: float | None = None
    amountAvailable: float | None = None
