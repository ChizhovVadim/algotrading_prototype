from tests.domain import DateSum
from . import moex


def singleContractHprs(
        indBuilder,
        candleStorage,
        secCode: str,
        slippage: float,
        skipPnl,
) -> list[DateSum]:
    """Вычисляет дневные доходности советника.
    Есть 2 способоа вычислять доходность за день. 
    1. Прибыль сбрасываем по окончании основной сессии. Тогда доходности будут похожи на отчет брокера, тк клиринг идет по окончании основной сессии.
    2. Прибыль сбрасываем на открытии основной сессии. Будет больше похоже на правду, тк размер позиции пересчитываем на открытии основной сессии.
    """
    return computeDailyPnls2(candleStorage.read(secCode), indBuilder(), slippage, skipPnl)


def computeDailyPnls2(candles, ind, slippage: float, skipPnl):
    res = []
    pnl = 0.0
    prevPosition = 0.0
    baseCandle = None
    prevCandle = None
    for candle in candles:
        if not ind.add(candle.dateTime, candle.closePrice):
            continue
        # Для совершения сделок робот включен только в основную сессию
        if not moex.isMainFortsSession(candle.dateTime):
            continue

        newPosition = ind.value()
        if prevCandle is not None:
            # Хотим на длинные выходные сокращать или закрывать позиции. TODO skipPnlRatio?
            if skipPnl is None or not skipPnl(prevCandle.dateTime, candle.dateTime):
                pnl += prevPosition * (candle.closePrice - prevCandle.closePrice) - \
                    slippage*abs(newPosition-prevPosition)*candle.closePrice

            # Открытие основной сессии нового дня
            if prevCandle.dateTime.date() != candle.dateTime.date():
                if baseCandle is not None:
                    hpr = 1.0+pnl/baseCandle.closePrice
                    if hpr <= 0:
                        raise ValueError("hpr <= 0")
                    res.append(DateSum(baseCandle.dateTime.date(), hpr))
                baseCandle = candle  # база - открытие основной сессии нового дня
                pnl = 0

        prevPosition = newPosition
        prevCandle = candle

    # Добавлять pnl не завершенного дня
    if baseCandle is not None:
        hpr = 1.0+pnl/baseCandle.closePrice
        if hpr <= 0:
            raise ValueError("hpr <= 0")
        res.append(DateSum(baseCandle.dateTime.date(), hpr))

    return res
