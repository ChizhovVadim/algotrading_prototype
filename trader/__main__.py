"""
Автоторговля торговых советников
"""

import threading
import logging
import os
import datetime

from advisors import AdvisorBuilder
from historydata import CandleStorage
from . import brokers, usercommands, moex, strategies, settings
from .trader import Trader
from .strategies.signal import SignalService
from .strategies.strategy import StrategyService


def main():
    initLogger()
    logging.info("Application started.")
    trader = Trader()
    try:
        configureTrader(trader)
        usercmd_thread = threading.Thread(
            target=usercommands.handle, args=[trader._inbox])
        usercmd_thread.start()
        trader.run()
    finally:
        trader.close()


def configureTrader(trader: Trader):
    portfolios = settings.portfolios
    activeBrokers = {p.clientKey for p in portfolios}
    if settings.marketData:
        activeBrokers.add(settings.marketData)

    for brokerConfig in settings.brokerConfigs:
        brokerKey = brokerConfig["key"]
        if brokerKey not in activeBrokers:
            continue
        broker = brokers.build(trader._inbox, **brokerConfig)
        trader._broker.add(brokerKey, broker)

    marketData = trader._broker.get(settings.marketData)

    signalServices = [buildSignal(
        marketData, **signalConfig) for signalConfig in settings.signalConfigs]

    # Каждый сигнал торгуем в каждом портфеле
    strategyServices = [StrategyService(trader._broker, portfolio, signal._security, signal._name)
                        for signal in signalServices
                        for portfolio in portfolios]

    trader._signalManager._signals.extend(signalServices)
    trader._portfolioManager._portfolios.extend(portfolios)
    trader._strategyManager._strategies.extend(strategyServices)


def buildSignal(marketData,
                security: str, name: str, stdVol: float, candleInterval: str, sizeConfig):
    sec = moex.getSecurityInfo(security)
    ind = AdvisorBuilder(name, stdVol).build()
    signalService = SignalService(
        marketData, name, ind, sec, candleInterval, sizeConfig)
    candleStorage = CandleStorage.FromCandleInterval(
        settings.candleFolder, candleInterval)
    signalService.applyHistoryCandles(candleStorage.read(security))
    return signalService


def initLogger():
    today = datetime.date.today()
    logPath = os.path.join(
        settings.logFolder,
        f"{today.strftime('%Y-%m-%d')}.txt")
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
        level=logging.DEBUG,
        handlers=[
            consoleHandler,
            logging.FileHandler(logPath),
        ])


main()
