import datetime
import unittest
from domaintypes import Security

TIMEZONE = datetime.timezone(datetime.timedelta(hours=+3), name="MSK")

FUTURESCLASSCODE = "SPBFUT"


class HardCodeSecurityInfoService:
    def __init__(self):
        pass

    def getSecurityInfo(self, securityName: str) -> Security:
        if securityName.startswith("Si"):
            return Security(
                name=securityName,
                classCode=FUTURESCLASSCODE,
                code=_encodeSecurity(securityName),
                pricePrecision=0,
                priceStep=1,
                priceStepCost=1,
                lever=1,
            )
        if securityName.startswith("CNY"):
            return Security(
                name=securityName,
                classCode=FUTURESCLASSCODE,
                # можно здесь replace("CNY", "CR")
                code=_encodeSecurity(securityName),
                pricePrecision=3,
                priceStep=0.001,
                priceStepCost=1,
                lever=1000,
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
