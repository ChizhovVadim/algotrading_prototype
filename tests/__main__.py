"""
Тестирование торговых советников на исторических данных
"""


import os
import argparse
import datetime
import time

from historydata import CandleStorage
from advisors import AdvisorBuilder
from . import moex, pnlmulty, pnlstat, risk, calendar


def mainHandler():
    "Проверяем торговую систему на исторических данных."
    today = datetime.date.today()

    parser = argparse.ArgumentParser()
    parser.add_argument('--advisor', type=str, default="main")
    parser.add_argument('--timeframe', type=str, default="minutes5")
    parser.add_argument('--security', type=str, default="Si")
    parser.add_argument('--lever', type=float)
    parser.add_argument('--slippage', type=float, default=0.03 * 0.01)
    parser.add_argument('--single', action="store_true")
    parser.add_argument('--startyear', type=int, default=today.year)
    parser.add_argument('--startquarter', type=int, default=0)
    parser.add_argument('--finishyear', type=int, default=today.year)
    parser.add_argument('--finishquarter', type=int, default=3)
    args = parser.parse_args()

    if args.single:
        secCodes = [args.security]
    else:
        secCodes = moex.quarterSecurityCodes(args.security,
                                             moex.TimeRange(args.startyear, args.startquarter, args.finishyear, args.finishquarter))

    candleStorage = CandleStorage.FromCandleInterval(
        os.path.expanduser("~/TradingData"), args.timeframe)

    indBuilder = AdvisorBuilder(args.advisor, None).build

    start = time.time()
    pnls = pnlmulty.multiContractHprs(
        indBuilder, candleStorage, secCodes, args.slippage, calendar.afterLongHoliday)
    lever = args.lever or risk.optimalLever(pnls, risk.limitStdev(0.045))
    pnls = risk.applyLever(pnls, lever)
    print(f"Плечо {lever:.1f}")
    pnlstat.computeAndPrint(pnls)
    print(f"Elapsed: {(time.time()-start):.2f}")


mainHandler()
