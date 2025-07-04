
def applyCandleValidation(advisor):
    lastCandle = None

    def f(candle):
        nonlocal lastCandle
        if lastCandle is not None and candle.DateTime <= lastCandle.DateTime:
            return None
        lastCandle = candle
        return advisor(candle)
    return f
