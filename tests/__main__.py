"""
Тестирование торговых советников на исторических данных
"""


import os
import argparse
import datetime
import time

from historydata import CandleStorage, CandleInterval
from advisors import AdvisorBuilder
from . import advisorpnls, equityreport


def mainHandler():
    "Проверяем торговую систему на исторических данных."
    today = datetime.date.today()

    parser = argparse.ArgumentParser()
    parser.add_argument('--advisor', type=str, default="main")
    parser.add_argument('--timeframe', type=str, default=CandleInterval.Minutes5)
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
        secCodes = advisorpnls.quarterSecurityCodes(args.security,
                                                    advisorpnls.TimeRange(args.startyear, args.startquarter, args.finishyear, args.finishquarter))

    candleStorage = CandleStorage.FromCandleInterval(
        os.path.expanduser("~/TradingData"), args.timeframe)

    indBuilder = AdvisorBuilder(args.advisor, None).build

    start = time.time()
    pnls = advisorpnls.multiContractHprs(
        indBuilder, candleStorage, secCodes, args.slippage, advisorpnls.afterLongHoliday)
    lever = args.lever or equityreport.optimalLever(
        pnls, equityreport.limitStdev(0.045))
    pnls = equityreport.applyLever(pnls, lever)
    print(f"Плечо {lever:.1f}")
    equityreport.computeAndPrint(pnls)
    print(f"Elapsed: {(time.time()-start):.2f}")


mainHandler()
