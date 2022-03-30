from decimal import Decimal


def toDecimal(num):
    if isinstance(num, float):
        return Decimal(str(num))
    if isinstance(num, str) or isinstance(num, int):
        return Decimal(num)
    if isinstance(num, Decimal):
        return num