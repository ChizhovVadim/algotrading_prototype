import logging
import datetime
import os
import threading

from . import settings
from historydata.model import CandleInterval
from historydata.candlestorage import CandleStorage
from trading.engine import Engine
from trading.monitoring import MonitoringService
from trading.signal import SignalService
from trading.strategy import StrategyService, SizePolicy
from trading.usercommand import readUserCommands
from trading import moex
from broker.model import Portfolio
from broker.multybroker import MultyBroker
from broker.mockbroker import MockBroker
from advisor.build import AdvisorBuilder


def main():
    "Автоторговля торговых советников"
    initLogger()
    logging.info("Application started.")
    multyBroker = MultyBroker()
    try:
        monitoring = MonitoringService(multyBroker)
        eng = Engine(monitoring)
        configure(multyBroker, eng)
        multyBroker.init()
        usercmd_thread = threading.Thread(target=readUserCommands, args=[eng.send])
        usercmd_thread.start()
        eng.run()
    finally:
        multyBroker.close()


def initLogger():
    today = datetime.date.today()
    os.makedirs(settings.logFolder, exist_ok=True)
    logPath = os.path.join(settings.logFolder, f"{today.strftime('%Y-%m-%d')}.txt")
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
        level=logging.DEBUG,
        handlers=[
            consoleHandler,
            logging.FileHandler(logPath),
        ],
    )


def configure(multyBroker: MultyBroker, eng: Engine):
    # Для простоты настройки прямо в коде

    # brokers
    multyBroker.add("paper", MockBroker("paper"))
    marketData = multyBroker.get("paper")

    # Чтобы проверить без квика
    if False:
        from broker.quikbroker import QuikBroker

        multyBroker.add("quik", QuikBroker(34128, eng.send))
        marketData = multyBroker.get("quik")

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
            AdvisorBuilder(advisor, None).build(),
            security,
            candleInterval,
        )
        signal.applyHistoryCandles(candleStorage.read(securityName))
        eng._signals.append(signal)

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
                multyBroker, portfolio, security, signalName, sizePolicy
            )
            eng._strategies.append(startegy)


if __name__ == "__main__":
    main()
