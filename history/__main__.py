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
    parser.add_argument('--startyear', type=int)
    parser.add_argument('--startquarter', type=int)
    parser.add_argument('--lever', type=float)
    parser.add_argument('--single', action="store_true")
    # TODO endquarter
    # TODO slippage
    args = parser.parse_args()

    reportAdvisor(args.advisor, args.timeframe, args.security, args.lever, None,
                  args.startyear, args.startquarter, None, None, args.single)


def main():
    start = time.time()
    historyHandler()
    print(f"Elapsed: {(time.time()-start):.2f}")


main()
