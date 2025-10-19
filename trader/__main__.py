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
    trader._broker.add("paper", MockBroker("paper"))
    marketData = trader._broker.get("paper")

    # TODO activeBrokers
    # Чтобы проверить код без квика
    if False:
        trader._broker.add("myquik", QuikBroker(34128, trader._inbox))
        marketData = trader._broker.get("myquik")

    signalServices = [
        configureSignal("CNY-12.25", "sample", 0.006, "minutes5",
                        strategies.SizeConfig(9, 9, 9, 0.6), marketData),
        configureSignal("Si-12.25", "sample", 0.006, "minutes5",
                        strategies.SizeConfig(9, 9, 6, 0.4), marketData),
    ]
    portfolios = [
        Portfolio(
            clientKey="paper",
            firm="",
            portfolio="test",
            amountWeight=None,
            amountUpper=None,
            amountAvailable=None,
        ),
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
