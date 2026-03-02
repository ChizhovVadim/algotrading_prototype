import collections

from domain.model.candle import CandleStorage
from domain.advisor import AdvisorBuilder


def advisorStatusUsecase(
    candleStorage: CandleStorage,
    advisor: str,
    security: str,
    count: int,
):
    ind = AdvisorBuilder(advisor, None).build()
    advices = collections.deque(maxlen=count)
    for candle in candleStorage.read(security):
        ind.add(candle.dateTime, candle.closePrice)
        pos = ind.value()
        if len(advices) == 0 or advices[-1] != pos:
            advices.append(pos)

    print(security, advisor, advices)
