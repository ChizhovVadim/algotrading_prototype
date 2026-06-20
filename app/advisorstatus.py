import argparse

from app import settings
from historydata.model import CandleInterval
from historydata.candlestorage import CandleStorage
from advisorstatus import advisorStatusUsecase
from advisor.build import AdvisorBuilder


def main():
    "Текущая позиция торговой системы."
    parser = argparse.ArgumentParser()
    parser.add_argument("--advisor", type=str, default="main")
    parser.add_argument("--advisorsettings", type=str)
    parser.add_argument("--timeframe", type=str, default=CandleInterval.Minutes5)
    parser.add_argument("--security", type=str, required=True)
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    candleStorage = CandleStorage.FromCandleInterval(
        settings.candleFolder, args.timeframe
    )
    advisor = AdvisorBuilder(args.advisor, args.advisorsettings).build()
    advisorStatusUsecase(candleStorage, advisor, args.security, args.count)


if __name__ == "__main__":
    main()
