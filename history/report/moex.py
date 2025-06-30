import datetime
from typing import NamedTuple

class TimeRange(NamedTuple):
	StartYear:     int
	StartQuarter:  int
	FinishYear:    int
	FinishQuarter: int

def quarterSecurityCodes(name: str, tr: TimeRange)-> list[str]:
	res = []
	for year in range(tr.StartYear, tr.FinishYear+1):
		for quarter in range(0, 4):
			if year == tr.StartYear:
				if quarter<tr.StartQuarter:
					continue
			if year == tr.FinishYear:
				if quarter>tr.FinishQuarter:
					break
			res.append(f"{name}-{3+quarter*3}.{year%100:02}")
	return res

def approxExpirationDate(securityCode: str)-> datetime.datetime:
	# С 1 июля 2015, для новых серий по кот нет открытых позиций, все основные фьючерсы и опционы должны исполняться в 3-й четверг месяца
	# name-month.year
	delim1 = securityCode.index("-")
	delim2 = securityCode.index(".")
	month = int(securityCode[delim1+1:delim2])
	curYear = datetime.datetime.today().year
	year = int(securityCode[delim2+1:])+curYear-curYear%100
	return datetime.datetime(year, month, 15)
