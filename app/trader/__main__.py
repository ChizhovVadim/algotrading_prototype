import logging
import os
import datetime

import settings
from .traderapp import TraderApp
from .configure import configure


def main():
    "Автоторговля торговых советников"
    initLogger()
    logging.info("Application started.")
    trader = TraderApp()
    try:
        configure(trader)
        trader.run()
    finally:
        trader.close()


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


main()
