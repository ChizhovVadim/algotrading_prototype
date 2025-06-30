import os
import datetime

import domaintypes
from history.candlestorage import CandleStorage
from .import moex
from . import dateutils
from . import leverutils
from . import statistic
from .hpr import multiContractHprs


def reportAdvisor(
        advisor: str,
        timeframe: str | None,
        security: str,
        lever: float | None,
        slippage: float | None,
        startYear: int,
        startQuarter: int,
        finishYear: int,
        finishQuarter: int,
        singleContract: bool,
):
    today = datetime.datetime.today()

    if slippage is None:
        slippage = 0.03 * 0.01
    if startYear is None:
        startYear = today.year
    if startQuarter is None:
        startQuarter = 0
    if finishYear is None:
        finishYear = today.year
    if finishQuarter is None:
        finishQuarter = 2#TODO

    candleInterval = domaintypes.CandleInterval.MINUTES5
    candlesPath = os.path.expanduser("~/TradingData")
    candleStorage = CandleStorage(candlesPath, candleInterval)

    if singleContract:
        tickers = [security]
    else:
        tickers = moex.quarterSecurityCodes(
            security, moex.TimeRange(startYear, startQuarter, finishYear, finishQuarter))

    hprs = multiContractHprs(advisor, candleStorage,
                             tickers, slippage, dateutils.afterLongHoliday)
    lever = lever or leverutils.optimalLever(
        hprs, leverutils.limitStdev(0.045))
    hprs = leverutils.applyLever(hprs, lever)
    stat = statistic.computeHprStatistcs(hprs)

    print(f"Отчет {advisor} {security}")
    print(f"Плечо {lever:.1f}")
    statistic.printReport(stat)
