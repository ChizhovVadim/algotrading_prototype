import os

from .strategies.domain import Portfolio
from .strategies.signal import SizeConfig

logFolder = os.path.expanduser("~/TradingData/Logs/luatrader/python")
candleFolder = os.path.expanduser("~/TradingData")
useCandleStorage = True

signalConfigs = [
    {"security": "CNY-12.25",
     "name": "sample",
     "stdVol": 0.006,
     "candleInterval": "minutes5",
     "sizeConfig": SizeConfig(longLever=9, shortLever=9, maxLever=9, weight=0.6),
     },
    {"security": "Si-12.25",
     "name": "sample",
     "stdVol": 0.006,
     "candleInterval": "minutes5",
     "sizeConfig": SizeConfig(longLever=9, shortLever=9, maxLever=6, weight=0.4),
     },
]

marketData = "paper"

portfolios = [
    Portfolio(clientKey="paper", firm="", portfolio="test"),
]

brokerConfigs = [
    {"key": "paper", "type": "mock"},
    {"key": "vadim", "type": "quik", "port": 34128},
]
