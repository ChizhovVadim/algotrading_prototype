import logging
import os
import datetime
import threading

import settings
import infra.usercommands
from infra.candlestorage import CandleStorage
from infra.mockbroker import MockBroker
from infra import moex
from domain.model.candle import CandleInterval
from domain.trader import Trader, Portfolio, PortfolioService, SignalService, SizeConfig
from domain.advisor import AdvisorBuilder


def main():
    "Автоторговля торговых советников"
    initLogger()
    logging.info("Application started.")
    trader = Trader()
    try:
        configureTrader(trader)
        usercmd_thread = threading.Thread(
            target=infra.usercommands.read, args=[trader._inbox]
        )
        usercmd_thread.start()
        trader.run()
    finally:
        trader.close()


def configureTrader(trader: Trader):
    # Для простоты настройки прямо в коде

    # brokers
    trader._broker.add("paper", MockBroker("paper"))
    marketData = trader._broker.get("paper")

    candleStorage = CandleStorage.FromCandleInterval(
        settings.candleFolder, CandleInterval.Minutes5
    )

    # signals
    trader._signals.append(
        buildSignal(
            candleStorage,
            marketData,
            "CNY-3.26",
            "main",
            0.006,
            CandleInterval.Minutes5,
            SizeConfig(9, 9, 9, 0.6),
        )
    )
    trader._signals.append(
        buildSignal(
            candleStorage,
            marketData,
            "Si-3.26",
            "main",
            0.006,
            CandleInterval.Minutes5,
            SizeConfig(9, 9, 6, 0.4),
        )
    )

    # portfolios
    trader._portfolios.append(
        PortfolioService(trader._broker, Portfolio("paper", "", "test"))
    )

    # strategies
    trader.addStrategiesForAllSignalPortfolioPairs()


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


def initLogger():
    today = datetime.date.today()
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


if __name__ == "__main__":
    main()
