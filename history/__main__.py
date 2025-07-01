import argparse
import logging
import time

from .report.history import reportAdvisor


def historyHandler():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--advisor', type=str, required=True)
    parser.add_argument('--timeframe', type=str)
    parser.add_argument('--security', type=str, required=True)
    parser.add_argument('--lever', type=float)
    parser.add_argument('--slippage', type=float)
    parser.add_argument('--single', action="store_true")
    parser.add_argument('--startyear', type=int)
    parser.add_argument('--startquarter', type=int)
    parser.add_argument('--finishyear', type=int)
    parser.add_argument('--finishquarter', type=int)

    args = parser.parse_args()

    reportAdvisor(args.advisor, args.timeframe, args.security, args.lever, args.slippage,
                  args.startyear, args.startquarter, args.finishyear, args.finishquarter, args.single)


def main():
    start = time.time()
    historyHandler()
    print(f"Elapsed: {(time.time()-start):.2f}")


main()
