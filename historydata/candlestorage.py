import datetime
import csv
import os

from .domain import Candle


class CandleStorage:

    def FromCandleInterval(baseFolder: str, candleInterval: str):
        folderPath = os.path.join(baseFolder, candleInterval)
        return CandleStorage(folderPath)

    def __init__(self, historyCandlesFolder: str):
        self._historyCandlesFolder = historyCandlesFolder

    def _fileName(self, securityCode: str):
        return os.path.join(self._historyCandlesFolder, securityCode+".txt")

    def _parseCandle(self, row, securityCode: str) -> Candle:
        dt = datetime.datetime.strptime(row[2], "%Y%m%d")
        t = int(row[3])

        hour = t // 10000
        min = (t // 100) % 100
        dt = dt + datetime.timedelta(hours=hour, minutes=min)

        o = float(row[4])
        h = float(row[5])
        l = float(row[6])
        c = float(row[7])
        v = float(row[8])
        return Candle(securityCode, dt, o, h, l, c, v)

    def read(self, securityCode: str):
        with open(self._fileName(securityCode), 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',',)
            # skip header
            next(reader)
            for row in reader:
                yield self._parseCandle(row, securityCode)
