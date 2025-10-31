import argparse
import os
import collections

from historydata import CandleStorage, CandleInterval
from advisors import AdvisorBuilder


def recentAdvices(
        ind,
        candles,
        count: int,
):
    advices = collections.deque(maxlen=count)
    for candle in candles:
        ind.add(candle.dateTime, candle.closePrice)
        pos = ind.value()
        if len(advices) == 0 or advices[-1] != pos:
            advices.append(pos)
    return advices


# python3 -m history.status --security Si-12.25
def statusHandler():
    "Текущая позиция торговой системы."
    parser = argparse.ArgumentParser()
    parser.add_argument('--advisor', type=str, default="main")
    parser.add_argument('--timeframe', type=str, default=CandleInterval.Minutes5)
    parser.add_argument('--security', type=str, required=True)
    parser.add_argument('--count', type=int, default=1)
    args = parser.parse_args()

    ind = AdvisorBuilder(args.advisor, None).build()
    candleStorage = CandleStorage.FromCandleInterval(
        os.path.expanduser("~/TradingData"), args.timeframe)
    advices = recentAdvices(ind, candleStorage.read(args.security), args.count)
    print(args.security, args.advisor, advices)


if __name__ == "__main__":
    statusHandler()
