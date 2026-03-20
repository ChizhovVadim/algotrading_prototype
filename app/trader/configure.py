import logging

import settings
from infra.candlestorage import CandleStorage
from infra import moex
from domain.trading.mockbroker import MockBroker
from domain.trading.signal import SignalService
from domain.trading.strategy import StrategyService, SizePolicy
from domain.model.candle import Candle, CandleInterval
from domain.model.broker import Portfolio
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

    signalConfigs = [
        {
            "advisor": "main",
            "security": "CNY-6.26",
            "longlever": 9.0,
            "shortlever": 9.0,
            "maxlever": 9.0,
            "weight": 0.6,
        },
        {
            "advisor": "main",
            "security": "Si-6.26",
            "longlever": 9.0,
            "shortlever": 9.0,
            "maxlever": 6.0,
            "weight": 0.4,
        },
    ]
    portfolioConfigs = [
        {
            "portfolio": Portfolio("paper", "SPBFUT", "test"),
        },
    ]

    for signalConfig in signalConfigs:
        advisor = signalConfig["advisor"]
        securityName = signalConfig["security"]
        signalName = f"{advisor}-{securityName}"
        security = moex.getSecurityInfo(securityName)
        signal = SignalService(
            marketData,
            signalName,
            AdvisorBuilder(advisor, 0.006).build(),
            security,
            candleInterval,
        )
        signal.applyHistoryCandles(candleStorage.read(securityName))
        trader._signals.append(signal)

        # Каждый сигнал торгуем в каждом портфеле
        for portfolioConfig in portfolioConfigs:
            portfolio = portfolioConfig["portfolio"]
            sizePolicy = SizePolicy(
                signalConfig["longlever"],
                signalConfig["shortlever"],
                signalConfig["maxlever"],
                signalConfig["weight"],
            )
            startegy = StrategyService(
                trader._broker, portfolio, security, signalName, sizePolicy
            )
            trader._strategies.append(startegy)
