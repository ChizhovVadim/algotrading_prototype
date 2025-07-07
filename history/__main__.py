import argparse
import logging
import time
import sys

from .report import history


def statusHandler(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--advisor', type=str, required=True)
    parser.add_argument('--timeframe', type=str)
    parser.add_argument('--security', type=str, required=True)
    parser.add_argument('--count', type=int)
    args = parser.parse_args(args)

    history.reportStatus(args.advisor, args.timeframe,
                         args.security, args.count)


def historyHandler(args):
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

    args = parser.parse_args(args)

    start = time.time()
    history.reportAdvisor(args.advisor, args.timeframe, args.security, args.lever, args.slippage,
                          args.startyear, args.startquarter, args.finishyear, args.finishquarter, args.single)
    print(f"Elapsed: {(time.time()-start):.2f}")


def main():
    cmd = sys.argv[1] if len(sys.argv) >= 2 else None
    if cmd == "status":
        statusHandler(sys.argv[2:])
    else:
        historyHandler(sys.argv[1:])


main()
