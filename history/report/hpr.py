import itertools
import multiprocessing

import advisors
from history.candlestorage import CandleStorage
from .datesum import DateSum
from . import dateutils


def singleContractHprs(args) -> list[DateSum]:
    (advisorName, candleStorage, secCode, slippage, skipPnl) = args
    return calcDailyPeriodResults(
        advisors.buildAdvisor(advisorName),
        candleStorage.read(secCode),
        slippage,
        skipPnl)


def multiContractHprs(
    advisorName: str,
        candleStorage: CandleStorage,
        secCodes: list[str],
        slippage: float,
        skipPnl,
) -> list[DateSum]:
    "Вычисляет дневные доходности советника по серии контрактов"
    parallel = True

    if parallel:
        hprByContract = []
        with multiprocessing.Pool() as pool:
            args = ((advisorName, candleStorage, secCode, slippage, skipPnl)
                    for secCode in secCodes)
            for hprs in pool.map(singleContractHprs, args):
                hprByContract.append(hprs)
        return concatHprs(hprByContract)
    else:
        hprByContract = []
        for secCode in secCodes:
            args = (advisorName, candleStorage, secCode, slippage, skipPnl)
            hprByContract.append(singleContractHprs(args))
        return concatHprs(hprByContract)


def calcDailyPeriodResults(
        advisor,
        candles,
        slippage: float,
        skipPnl,
) -> list[DateSum]:
    "По советнику на исторических барах вычисляет дневные доходности"

    res = []
    pnl = 0.0
    baseAdvice = None
    lastAdvice = None

    for candle in candles:
        advice = advisor(candle)
        if advice is None:
            continue

        if baseAdvice is None:
            baseAdvice = advice
            lastAdvice = advice
            continue

        # TODO проверить, что skipPnl и новый день согласованы.
        if dateutils.isNewFortsDateStarted(lastAdvice.dateTime, advice.dateTime):
            res.append(DateSum(lastAdvice.dateTime.date(),
                       1 + pnl/baseAdvice.price))
            pnl = 0.0
            baseAdvice = lastAdvice
        if not skipPnl(lastAdvice.dateTime, advice.dateTime):
            pnl += (lastAdvice.position*(advice.price-lastAdvice.price) -
                    slippage*advice.price*abs(advice.position-lastAdvice.position))
        lastAdvice = advice

    if lastAdvice is not None:
        res.append(DateSum(lastAdvice.dateTime.date(),
                   1 + pnl/baseAdvice.price))

    return res


def concatHprs(hprByContract: list[list[DateSum]]) -> list[DateSum]:
    "Объединияет дневные доходности по разным контрактам"

    res = []
    for hprs in hprByContract:
        if not hprs:
            continue
        if res:
            # последний день предыдущего контракта может быть не полный
            res.pop()
        if res:
            lastDate = res[-1].date
            # or x.Date<lastDate
            res.extend(itertools.dropwhile(lambda x: x.date <= lastDate, hprs))
        else:
            res.extend(hprs)
    return res
