
def applyCandleValidation(advisor):
    lastCandle = None

    def f(candle):
        nonlocal lastCandle
        if lastCandle is not None and candle.dateTime <= lastCandle.dateTime:
            return None
        lastCandle = candle
        return advisor(candle)
    return f
