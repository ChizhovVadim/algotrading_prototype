"""
Автоторговля торговых советников
"""

import threading
import logging
import os
import datetime

from advisors import AdvisorBuilder
from historydata import CandleStorage
from .brokers.mockbroker import MockBroker
from .domain import MarketDataService
from . import usercommands, moex, strategies, settings


def main():
    initLogger()
    logging.info("Application started.")
    trader = strategies.Trader()
    try:
        configureTrader(trader)
        usercmd_thread = threading.Thread(
            target=usercommands.handle, args=[trader._inbox])
        usercmd_thread.start()
        trader.run()
    finally:
        trader.close()


def configureTrader(trader: strategies.Trader):
    portfolios = settings.portfolios
    activeBrokers = {p.clientKey for p in portfolios}

    marketData = None
    for brokerConfig in settings.brokerConfigs:
        brokerKey = brokerConfig["key"]
        if brokerKey not in activeBrokers:
            continue
        broker = buildBroker(trader._inbox, **brokerConfig)
        trader._broker.add(brokerKey, broker)
        if marketData is None:
            logging.info(f"MarketData {brokerKey}")
            marketData = broker

    signalServices = [buildSignal(
        marketData, **signalConfig) for signalConfig in settings.signalConfigs]

    # Каждый сигнал торгуем в каждом портфеле
    strategyServices = [strategies.StrategyService(trader._broker, portfolio, signal._security, signal._name)
                        for signal in signalServices
                        for portfolio in portfolios]

    trader._signalManager._signals.extend(signalServices)
    trader._portfolioManager._portfolios.extend(portfolios)
    trader._strategyManager._strategies.extend(strategyServices)


def buildBroker(marketDataQueue, key, type, **kwargs):
    if type == "mock":
        return MockBroker(key)
    elif type == "quik":
        from .brokers.quikbroker import QuikBroker
        return QuikBroker(kwargs["port"], marketDataQueue)
    else:
        # кроме quik можно поддержать API finam/alor/T.
        raise ValueError("bad broker type", type)


def buildSignal(marketData: MarketDataService,
                security: str, name: str, stdVol: float, candleInterval: str, sizeConfig: strategies.SizeConfig):
    sec = moex.getSecurityInfo(security)
    ind = AdvisorBuilder(name, stdVol).build()
    signalService = strategies.SignalService(
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
