from .mockbroker import MockBroker


def build(marketDataQueue, key: str, type: str, **kwargs):
    if type == "mock":
        return MockBroker(key)
    elif type == "quik":
        from .quikbroker import QuikBroker
        return QuikBroker(kwargs["port"], marketDataQueue)
    else:
        # кроме quik можно поддержать API finam/alor/T.
        raise ValueError("bad broker type", type)
