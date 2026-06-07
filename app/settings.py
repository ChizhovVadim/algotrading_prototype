import datetime
import os

displayDateLayout = "%d.%m.%Y"
TIMEZONE = datetime.timezone(datetime.timedelta(hours=+3), name="MSK")

candleFolder = os.path.expanduser("~/TradingData")
logFolder = os.path.expanduser("~/TradingData/Logs/luatrader/python")
