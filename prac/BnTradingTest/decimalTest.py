from decimal import Decimal


def test1():
    n1 = Decimal("-365.324552")
    n2 = Decimal('0.0003')
    n1 = n2 * (n1 // n2)
    print(n1)


if __name__ == '__main__':
    test1()