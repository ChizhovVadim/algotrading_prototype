import datetime
import csv
import os
from collections.abc import Generator

from domaintypes import Candle, CandleInterval


class CandleStorage:

    # candleInterval в конструктор, иначе пришлось бы добавлять его во все методы
    def __init__(self, historyCandlesFolder: str, candleInterval: CandleInterval):
        self._historyCandlesFolder = os.path.join(
            historyCandlesFolder, candleInterval)
        self._candleInterval = candleInterval

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
        return Candle(self._candleInterval, securityCode, dt, o, h, l, c, v)

    def read(self, securityCode: str) -> Generator[Candle]:
        with open(self._fileName(securityCode), 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',',)
            # skip header
            next(reader)
            for row in reader:
                yield self._parseCandle(row, securityCode)

    # Дописываем свечи в конец файла
    # TODO Если файл новый, то добавлять заголовок?
    def update(self, securityCode: str, candles: list[Candle]):
        path = self._fileName(securityCode)
        with open(path, 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for c in candles:
                data = [
                    securityCode,
                    "5",
                    c.DateTime.strftime("%Y%m%d"),
                    (c.DateTime.minute+100*c.DateTime.hour)*100,
                    c.OpenPrice,  # TODO f
                    c.HighPrice,
                    c.LowPrice,
                    c.ClosePrice,
                    c.Volume,
                ]
                writer.writerow(data)

    def last(self, securityCode: str) -> Candle:
        result = None
        for candle in self.read(securityCode):
            result = candle
        return result

    def candleByDate(self, securityCode: str, date: datetime.datetime) -> Candle:
        result = None
        for candle in self.read(securityCode):
            if candle.DateTime > date:
                break
            result = candle
        return result

    def candleBeforeDate(self, securityCode: str, date: datetime.datetime) -> Candle:
        result = None
        for candle in self.read(securityCode):
            if candle.DateTime >= date:
                break
            result = candle
        return result
