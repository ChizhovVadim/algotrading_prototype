import argparse

import settings
from domain.model.candle import CandleInterval
from infra.candlestorage import CandleStorage
from domain.advisorstatus import advisorStatusUsecase


def main():
    "Текущая позиция торговой системы."
    parser = argparse.ArgumentParser()
    parser.add_argument("--advisor", type=str, default="main")
    parser.add_argument("--timeframe", type=str, default=CandleInterval.Minutes5)
    parser.add_argument("--security", type=str, required=True)
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    candleStorage = CandleStorage.FromCandleInterval(
        settings.candleFolder, args.timeframe
    )

    advisorStatusUsecase(candleStorage, args.advisor, args.security, args.count)


if __name__ == "__main__":
    main()
