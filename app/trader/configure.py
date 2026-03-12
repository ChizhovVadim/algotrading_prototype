import logging

import settings
from infra.candlestorage import CandleStorage
from infra.mockbroker import MockBroker
from infra import moex
from domain.model.candle import Candle, CandleInterval
from domain.model.broker import Portfolio
from domain.strategymanager import (
    PortfolioService,
    SignalService,
    SizeConfig,
)
from domain.advisor import AdvisorBuilder
from .traderapp import TraderApp


def configure(trader: TraderApp):
    # Для простоты настройки прямо в коде

    # brokers
    trader._broker.add("paper", MockBroker("paper"))
    marketData = trader._broker.get("paper")

    # Чтобы проверить без квика
    if False:
        from infra.quikbroker import QuikBroker

        trader._broker.add("quik", QuikBroker(34128, trader._inbox))
        marketData = trader._broker.get("quik")

    candleInterval = CandleInterval.Minutes5

    candleStorage = CandleStorage.FromCandleInterval(
        settings.candleFolder, candleInterval
    )

    # signals
    trader._strategyManager._signals.append(
        buildSignal(
            candleStorage,
            marketData,
            "CNY-3.26",
            "main",
            0.006,
            candleInterval,
            SizeConfig(9, 9, 9, 0.6),
        )
    )
    trader._strategyManager._signals.append(
        buildSignal(
            candleStorage,
            marketData,
            "Si-3.26",
            "main",
            0.006,
            candleInterval,
            SizeConfig(9, 9, 6, 0.4),
        )
    )

    # portfolios
    trader._strategyManager._portfolios.append(
        PortfolioService(trader._broker, Portfolio("paper", "", "test"), None, None)
    )

    # strategies
    trader._strategyManager.addStrategiesForAllSignalPortfolioPairs()


def buildSignal(
    candleStorage,
    marketData,
    security: str,
    name: str,
    stdVol: float,
    candleInterval: str,
    sizeConfig,
):
    sec = moex.getSecurityInfo(security)
    ind = AdvisorBuilder(name, stdVol).build()
    signalService = SignalService(
        marketData, name, ind, sec, candleInterval, sizeConfig
    )
    if candleStorage is not None:
        signalService.applyHistoryCandles(candleStorage.read(security))
    return signalService
