import datetime
import logging

from trader import moex
from trader.connectors.QuikPy import QuikPy
from .domain import Portfolio, Security, Order, PortfolioLimits, Candle


class QuikBroker:

    def __init__(self, port: int, marketDataQueue):
        self._port = port
        self._marketDataQueue = marketDataQueue

        self._startCandles = datetime.datetime.now() + datetime.timedelta(days=-1)
        self._quik = None
        self._transId = 1  # TODO init

    def onNewCandle(self, data):
        candle = _parseQuikCandle(data["data"])
        # чтобы очередь не переполнялась старыми барами
        if candle.dateTime >= self._startCandles:
            self._marketDataQueue.put(candle)

    def init(self):
        # Игорь Чечет https://github.com/cia76/QuikPy
        # Есть также библиотеки для работы с finam, alor, T-invest: https://github.com/cia76?tab=repositories
        self._quik = QuikPy(requests_port=self._port,
                            callbacks_port=self._port+1)
        self._quik.OnNewCandle = self.onNewCandle
        logging.info("Init broker quik")

    def checkStatus(self):
        pass

    def close(self):
        if self._quik is not None:
            self._quik.CloseConnectionAndThread()

    def isConnected(self) -> bool:
        resp = self._quik.IsConnected()
        return resp["data"] == 1

    def getLastCandles(self, security: Security,
                       candleInterval: str):
        # Если не указывать размер, то может прийти слишком много баров и unmarshal большой json
        MaxBars = 5_000
        new_bars = self._quik.GetCandlesFromDataSource(
            security.classCode, security.code, _quikTimeframe(candleInterval), MaxBars)['data']
        new_bars = [_parseQuikCandle(c) for c in new_bars]
        # последний бар за сегодня может быть не завершен
        if new_bars and new_bars[-1].dateTime.date() == datetime.date.today():
            new_bars.pop()
        return new_bars

    def subscribeCandles(self, security: Security, candleInterval: str):
        logging.debug(f"subscribeCandles {security.code} {candleInterval}")
        self._quik.SubscribeToCandles(
            security.classCode, security.code, _quikTimeframe(candleInterval))

    def getPortfolioLimits(self, portfolio: Portfolio):
        resp = self._quik.GetPortfolioInfoEx(
            portfolio.firm, portfolio.portfolio, 0)
        start_limit_open_pos = float(resp["data"]["start_limit_open_pos"])
        used_lim_open_pos = float(resp["data"]["used_lim_open_pos"])
        varmargin = float(resp["data"]["varmargin"])
        fut_accured_int = float(resp["data"]["fut_accured_int"])
        return PortfolioLimits(start_limit_open_pos, used_lim_open_pos, varmargin, fut_accured_int)

    def getPosition(self, portfolio: Portfolio,
                    security: Security) -> float:
        if security.classCode == moex.FUTURESCLASSCODE:
            resp = self._quik.GetFuturesHolding(
                portfolio.firm, portfolio.portfolio, security.code, 0)
            data = resp.get("data")
            if data is None:
                logging.debug(f"Position {security.name} empty.")
                return 0.0
            return float(data["totalnet"])

        raise NotImplementedError()

    def registerOrder(self, order: Order):
        transaction = {  # Все значения должны передаваться в виде строк
            'ACTION': 'NEW_ORDER',
            'SECCODE': order.security.code,
            'CLASSCODE': order.security.classCode,
            'ACCOUNT': order.portfolio.portfolio,
            'PRICE': _formatPrice(order.price, order.security.pricePrecision, order.security.priceStep),
            'TRANS_ID': str(self._transId),
            'CLIENT_CODE': str(self._transId),
        }
        self._transId += 1
        if order.volume > 0:
            transaction['OPERATION'] = "B"
            transaction['QUANTITY'] = str(order.volume)
        else:
            transaction['OPERATION'] = "S"
            transaction['QUANTITY'] = str(-order.volume)

        self._quik.SendTransaction(transaction)


def _quikTimeframe(candleInterval: str):
    if candleInterval == "minutes5":
        return 5
    raise ValueError("timeframe not supported", candleInterval)


def _parseQuikDateTime(dt):
    return datetime.datetime(
        int(dt["year"]),
        int(dt["month"]),
        int(dt["day"]),
        int(dt["hour"]),
        int(dt["min"]),
        int(dt["sec"]))


def _parseQuikCandle(row):
    return Candle(
        interval="minutes5",  # TODO
        securityCode=row["sec"],
        dateTime=_parseQuikDateTime(row["datetime"]),
        openPrice=float(row["open"]),
        highPrice=float(row["high"]),
        lowPrice=float(row["low"]),
        closePrice=float(row["close"]),
        volume=float(row["volume"]))


def _formatPrice(price: float, pricePrecision: int, priceStep: float):
    if priceStep:
        price = round(price / priceStep) * priceStep
    return f"{price:.{pricePrecision}f}"
