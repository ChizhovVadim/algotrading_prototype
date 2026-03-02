import time

from domain.model.candle import CandleStorage
from domain.advisor import AdvisorBuilder
from . import advisorpnls, equityreport


def historyReportUsecase(candleStorage: CandleStorage, args):

    if args.single:
        secCodes = [args.security]
    else:
        secCodes = advisorpnls.quarterSecurityCodes(
            args.security,
            advisorpnls.TimeRange(
                args.startyear, args.startquarter, args.finishyear, args.finishquarter
            ),
        )

    indBuilder = AdvisorBuilder(args.advisor, None).build

    start = time.time()
    pnls = advisorpnls.multiContractHprs(
        indBuilder, candleStorage, secCodes, args.slippage, advisorpnls.afterLongHoliday
    )
    lever = args.lever or equityreport.optimalLever(
        pnls, equityreport.limitStdev(0.045)
    )
    pnls = equityreport.applyLever(pnls, lever)
    print(f"Плечо {lever:.1f}")
    equityreport.computeAndPrint(pnls)
    print(f"Elapsed: {(time.time()-start):.2f}")
