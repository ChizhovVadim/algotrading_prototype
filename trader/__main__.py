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
from .brokers.quikbroker import QuikBroker
from .domain import MarketDataService, Portfolio
from . import usercommands, moex, strategies


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
    brokerConfigs = [
        {"key": "paper", "type": "mock"},
        {"key": "vadim", "type": "quik", "port": 34128},
    ]
    portfolios = [
        Portfolio(clientKey="paper", firm="", portfolio="test"),
    ]

    activeBrokers = {p.clientKey for p in portfolios}
    marketData = None
    for brokerConfig in brokerConfigs:
        brokerKey = brokerConfig["key"]
        if brokerKey not in activeBrokers:
            continue
        brokerType = brokerConfig["type"]
        if brokerType == "mock":
            broker = MockBroker(brokerKey)
        elif brokerType == "quik":
            broker = QuikBroker(brokerConfig["port"], trader._inbox)
        else:
            # кроме quik можно поддержать API finam/alor/T.
            raise ValueError("bad BrokerConfig", brokerConfig)
        trader._broker.add(brokerKey, broker)
        if marketData is None:
            logging.info(f"MarketData {brokerKey}")
            marketData = broker

    signalServices = [
        configureSignal("CNY-12.25", "sample", 0.006, "minutes5",
                        strategies.SizeConfig(9, 9, 9, 0.6), marketData),
        configureSignal("Si-12.25", "sample", 0.006, "minutes5",
                        strategies.SizeConfig(9, 9, 6, 0.4), marketData),
    ]
    # Каждый сигнал торгуем в каждом портфеле
    strategyServices = [strategies.StrategyService(trader._broker, portfolio, signal._security, signal._name)
                        for signal in signalServices
                        for portfolio in portfolios]

    trader._signalManager._signals.extend(signalServices)
    trader._portfolioManager._portfolios.extend(portfolios)
    trader._strategyManager._strategies.extend(strategyServices)


def configureSignal(secName: str, signalName: str, stdVol: float, candleInterval: str, sizeConfig: strategies.SizeConfig, marketData: MarketDataService):
    sec = moex.getSecurityInfo(secName)
    ind = AdvisorBuilder(signalName, stdVol).build()
    signalService = strategies.SignalService(
        marketData, signalName, ind, sec, candleInterval, sizeConfig)
    candleStorage = CandleStorage.FromCandleInterval(
        os.path.expanduser("~/TradingData"), candleInterval)
    signalService.applyHistoryCandles(candleStorage.read(secName))
    return signalService


def initLogger():
    today = datetime.date.today()
    logPath = os.path.join(
        os.path.expanduser("~/TradingData/Logs/luatrader/python"),
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
