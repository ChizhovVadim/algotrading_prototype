import argparse
import datetime

from . import settings
from historydata.model import CandleInterval
from historydata.candlestorage import CandleStorage
from advisorreport import historyReportUsecase


def main():
    "Проверяем торговую систему на исторических данных."
    today = datetime.date.today()

    parser = argparse.ArgumentParser()
    parser.add_argument("--advisor", type=str, default="main")
    parser.add_argument("--timeframe", type=str, default=CandleInterval.Minutes5)
    parser.add_argument("--security", type=str, default="Si")
    parser.add_argument("--lever", type=float)
    parser.add_argument("--slippage", type=float, default=0.03 * 0.01)
    parser.add_argument("--single", action="store_true")
    parser.add_argument("--startyear", type=int, default=today.year)
    parser.add_argument("--startquarter", type=int, default=0)
    parser.add_argument("--finishyear", type=int, default=today.year + 1)
    parser.add_argument("--finishquarter", type=int, default=0)
    args = parser.parse_args()

    candleStorage = CandleStorage.FromCandleInterval(
        settings.candleFolder, args.timeframe
    )

    historyReportUsecase(candleStorage, args)


if __name__ == "__main__":
    main()
