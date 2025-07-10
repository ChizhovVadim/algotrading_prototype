import datetime
import logging
import queue

import domaintypes
from trader import moex
from .QuikPy import QuikPy


class QuikTrader(domaintypes.SupportsClose):

    def __init__(self, port: int, marketData: queue.Queue):
        # Игорь Чечет https://github.com/cia76/QuikPy
        # Есть также библиотеки для работы с finam, alor, T-invest: https://github.com/cia76?tab=repositories
        self._quik = QuikPy(requests_port=port, callbacks_port=port+1)

        start = datetime.datetime.now()
        startCandles = start + datetime.timedelta(days=-1)

        def onNewCandle(data):
            candle = _parseQuikCandle(data["data"])
            # чтобы очередь не переполнялась старыми барами
            if candle.dateTime >= startCandles:
                marketData.put(candle)

        self._quik.OnNewCandle = onNewCandle
        self._transId = 1  # TODO init

    def close(self):
        self._quik.CloseConnectionAndThread()

    def isConnected(self) -> bool:
        resp = self._quik.IsConnected()
        return resp["data"] == 1

    def getLastCandles(self, security: domaintypes.Security,
                       candleInterval: str) -> list[domaintypes.Candle]:
        # Если не указывать размер, то может прийти слишком много баров и unmarshal большой json
        MaxBars = 5_000
        new_bars = self._quik.GetCandlesFromDataSource(
            security.classCode, security.code, _quikTimeframe(candleInterval), MaxBars)['data']
        new_bars = [_parseQuikCandle(c) for c in new_bars]
        # последний бар за сегодня может быть не завершен
        if new_bars and new_bars[-1].dateTime.date() == datetime.date.today():
            new_bars.pop()
        return new_bars

    def subscribeCandles(self, security: domaintypes.Security, candleInterval: str):
        self._quik.SubscribeToCandles(
            security.classCode, security.code, _quikTimeframe(candleInterval))
    
    def getPortfolioLimits(self, portfolio: domaintypes.Portfolio) -> domaintypes.PortfolioLimits:
        resp = self._quik.GetPortfolioInfoEx(portfolio.firm, portfolio.portfolio, 0)
        start_limit_open_pos = float(resp["data"]["start_limit_open_pos"])
        used_lim_open_pos = float(resp["data"]["used_lim_open_pos"])
        varmargin = float(resp["data"]["varmargin"])
        fut_accured_int = float(resp["data"]["fut_accured_int"])
        return domaintypes.PortfolioLimits(start_limit_open_pos, used_lim_open_pos, varmargin, fut_accured_int)

    def getPosition(self, portfolio: domaintypes.Portfolio,
                    security: domaintypes.Security) -> float:
        if security.classCode == moex.FUTURESCLASSCODE:
            resp = self._quik.GetFuturesHolding(
                portfolio.firm, portfolio.portfolio, security.code, 0)
            data = resp.get("data")
            if data is None:
                logging.warning(f"Position {security.name} empty.")
                return 0.0
            return float(data["totalnet"])

        raise NotImplementedError()

    def registerOrder(self, order: domaintypes.Order):
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


def _parseQuikDateTime(dt) -> datetime.datetime:
    return datetime.datetime(
        int(dt["year"]),
        int(dt["month"]),
        int(dt["day"]),
        int(dt["hour"]),
        int(dt["min"]),
        int(dt["sec"]))


def _parseQuikCandle(row) -> domaintypes.Candle:
    return domaintypes.Candle(
        interval="minutes5",  # TODO
        securityCode=row["sec"],
        dateTime=_parseQuikDateTime(row["datetime"]),
        openPrice=float(row["open"]),
        highPrice=float(row["high"]),
        lowPrice=float(row["low"]),
        closePrice=float(row["close"]),
        volume=float(row["volume"]))


def _formatPrice(price: float, pricePrecision: int, priceStep: float) -> str:
    if priceStep:
        price = round(price / priceStep) * priceStep
    return f"{price:.{pricePrecision}f}"
