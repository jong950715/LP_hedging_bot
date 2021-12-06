from random import *
import time


class Calculator:
    def __init__(self, n1, n2, n3, n4):
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4

    def add(self):
        res = self.n1 + self.n2 + self.n3 + self.n4
        return res

    def product(self):
        pass

    def minus(self):
        pass


def fun_add(n1, n2, n3, n4):
    res = n1 + n2 + n3 + n4
    return res


def main():
    startTime = time.time()
    accum = 0
    for _ in range(1000000):
        n1 = randint(1, 100)
        n2 = randint(1, 100)
        n3 = randint(1, 100)
        n4 = randint(1, 100)
        cal = Calculator(n1, n2, n3, n4)
        accum += cal.add()
    finTime = time.time()
    print(finTime - startTime, accum)

    startTime = time.time()
    accum = 0
    for _ in range(1000000):
        n1 = randint(1, 100)
        n2 = randint(1, 100)
        n3 = randint(1, 100)
        n4 = randint(1, 100)
        cal = fun_add(n1, n2, n3, n4)
        accum += cal
    finTime = time.time()
    print(finTime - startTime, accum)

    startTime = time.time()
    accum = 0
    for _ in range(1000000):
        n1 = randint(1, 100)
        n2 = randint(1, 100)
        n3 = randint(1, 100)
        n4 = randint(1, 100)
        cal = Calculator(n1, n2, n3, n4)
        accum += cal.add()
    finTime = time.time()
    print(finTime - startTime, accum)

    startTime = time.time()
    accum = 0
    for _ in range(1000000):
        n1 = randint(1, 100)
        n2 = randint(1, 100)
        n3 = randint(1, 100)
        n4 = randint(1, 100)
        cal = fun_add(n1, n2, n3, n4)
        accum += cal
    finTime = time.time()
    print(finTime - startTime, accum)


if __name__ == "__main__":
    main()
