import argparse
from broker.QuikPy import QuikPy


def main():
    "Проверка работы Quik"
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()

    quik = QuikPy(requests_port=args.port, callbacks_port=args.port + 1)
    quik.MessageInfo("Где деньги, Лебовски?")
    quik.CloseConnectionAndThread()


if __name__ == "__main__":
    main()
