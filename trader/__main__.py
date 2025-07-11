import logging
import os
import datetime
import queue
import threading

import domaintypes
from . import moex

from history.candlestorage import CandleStorage

from .traders.quiktrader import QuikTrader
from .traders.multytrader import MultyTrader
from .traders.mocktrader import MockTrader

from .strategies.signalservice import SignalConfig, initSignal
from .strategies.strategymanager import StrategyManager
from .strategies.strategyservice import StrategyConfig, initStrategy
from .import usercommands


def initLogger():
    today = datetime.date.today()
    logPath = os.path.join(
        os.path.expanduser("~/TradingData/Logs/luatrader/python"),
        f"{today.strftime("%Y-%m-%d")}.txt")
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler(), logging.FileHandler(logPath)])


def initStrategies(trader: MultyTrader, strategyManager: StrategyManager, inbox: queue.Queue):
    # init traders
    trader.add(MockTrader(), "paper")
    marketDataService = trader.get("paper")

    # Чтобы проверить код без квика
    if False:
        trader.add(QuikTrader(34128, inbox), "myquik")
        marketDataService = trader.get("myquik")

    secInfoService = moex.HardCodeSecurityInfoService()

    # init signals
    candleStorage = None
    #candleStorage = CandleStorage(os.path.expanduser(
    #    "~/TradingData"), domaintypes.CandleInterval.MINUTES5)
    signalConfigs = [
        SignalConfig("sample_momentum", "CNY-9.25"),
        SignalConfig("sample_momentum", "Si-9.25"),
    ]
    for signalConfig in signalConfigs:
        strategyManager.addSignal(initSignal(
            secInfoService, marketDataService, candleStorage, signalConfig))

    # init strategies
    strategyConfigs = [
        StrategyConfig(
            advisor="sample_momentum",
            security="CNY-9.25",
            longLever=9.0,
            shortLever=9.0,
            maxLever=9.0,
            weight=0.6,
        ),
        StrategyConfig(
            advisor="sample_momentum",
            security="Si-9.25",
            longLever=9.0,
            shortLever=9.0,
            maxLever=7.0,
            weight=0.4,
        ),
    ]
    portfolio = domaintypes.Portfolio(
        clientKey="paper",
        firm="",
        portfolio="test",
        amountWeight=None,
        amountUpper=None,
        amountAvailable=None,
    )
    for strategyConfig in strategyConfigs:
        strategyManager.addStrategy(initStrategy(
            secInfoService, trader, portfolio, strategyConfig))


def main():
    initLogger()
    logging.info("Application started.")

    trader = MultyTrader()
    try:
        strategyManager = StrategyManager()
        inbox = queue.Queue()
        initStrategies(trader, strategyManager, inbox)
        usercmd_thread = threading.Thread(
            target=usercommands.handle, args=[inbox])
        usercmd_thread.start()
        strategyManager.run(inbox)

    finally:
        trader.close()
        logging.info("Application closed.")


main()
