import datetime
import unittest
from domaintypes import SecurityInfo

TIMEZONE = datetime.timezone(datetime.timedelta(hours=+3), name="MSK")

FUTURESCLASSCODE = "SPBFUT"


class HardCodeSecurityInfoService:
    def __init__(self):
        pass

    def getSecurityInfo(self, securityName: str) -> SecurityInfo:
        if securityName.startswith("Si"):
            return SecurityInfo(
                Name=securityName,
                ClassCode=FUTURESCLASSCODE,
                Code=_encodeSecurity(securityName),
                PricePrecision=0,
                PriceStep=1,
                PriceStepCost=1,
                Lever=1,
            )
        if securityName.startswith("CNY"):
            return SecurityInfo(
                Name=securityName,
                ClassCode=FUTURESCLASSCODE,
                # можно здесь replace("CNY", "CR")
                Code=_encodeSecurity(securityName),
                PricePrecision=3,
                PriceStep=0.001,
                PriceStepCost=1,
                Lever=1000,
            )
        return None


def _encodeSecurity(securityCode: str) -> str:
    """
    Sample: "Si-3.17" -> "SiH7"
    http://moex.com/s205
    """

    # TODO вечные фьючерсы
    # if strings.HasSuffix(securityName, "F") {
    # return securityName, nil
    # }

    monthCodes = "FGHJKMNQUVXZ"

    delim1 = securityCode.index("-")
    delim2 = securityCode.index(".")

    name = securityCode[:delim1]
    month = int(securityCode[delim1+1:delim2])
    year = int(securityCode[delim2+1:])

    # курс китайский юань – российский рубль
    if name == "CNY":
        name = "CR"

    return f"{name}{monthCodes[month-1]}{year % 10}"


class TestSecurity(unittest.TestCase):
    def test_securityEncode(self):
        self.assertEqual(_encodeSecurity("Si-9.25"), "SiU5")
        self.assertEqual(_encodeSecurity("CNY-12.25"), "CRZ5")
