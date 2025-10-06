import math


def moments(source):
    mean = 0.0
    n = 0
    M2 = 0.0

    for x in source:
        n += 1
        delta = x - mean
        mean += delta / n
        M2 += delta * (x - mean)

    if n == 0:
        return math.nan, math.nan

    stDev = math.sqrt(M2 / n)
    return (mean, stDev)


# Алгоритм вычисления среднеквадратического отклонения за один проход
# быстрее statistics.pstdev
def stDev(source):
    _, stDev = moments(source)
    return stDev
