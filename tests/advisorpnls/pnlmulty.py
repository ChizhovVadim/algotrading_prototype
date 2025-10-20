import itertools
import multiprocessing

from tests.domain import DateSum
from .pnl import singleContractHprs


def _singleContractHprs(args) -> list[DateSum]:
    (indBuilder, candleStorage, secCode, slippage, skipPnl) = args
    return singleContractHprs(indBuilder, candleStorage, secCode, slippage, skipPnl)


def multiContractHprs(
        indBuilder,
        candleStorage,
        secCodes: list[str],
        slippage: float,
        skipPnl,
) -> list[DateSum]:
    "Вычисляет дневные доходности советника по серии контрактов"
    parallel = True

    if parallel:
        hprByContract = []
        with multiprocessing.Pool() as pool:
            args = ((indBuilder, candleStorage, secCode, slippage, skipPnl)
                    for secCode in secCodes)
            for hprs in pool.map(_singleContractHprs, args):
                hprByContract.append(hprs)
        return concatHprs(hprByContract)
    else:
        hprByContract = []
        for secCode in secCodes:
            args = (indBuilder, candleStorage, secCode, slippage, skipPnl)
            hprByContract.append(_singleContractHprs(args))
        return concatHprs(hprByContract)


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
