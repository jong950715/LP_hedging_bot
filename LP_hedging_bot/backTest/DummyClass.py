from collections import defaultdict
from decimal import Decimal


class DummySocket:
    def __init__(self):
        self.orderBook = defaultdict(lambda: defaultdict(lambda: [[0, 0]] * 5))
        self.orderBook['USDT']['bid'][0][0] = Decimal('1')
        self.orderBook['USDT']['ask'][0][0] = Decimal('1')

    def setPrice(self, sym, price):
        self.orderBook[sym]['bid'][0][0] = price
        self.orderBook[sym]['ask'][0][0] = price

    # for dummy
    def getOrderBook(self):
        return self.orderBook

    async def awaitOrderBookUpdate(self):
        pass

    def clearAwaitEvent(self):
        pass


class DummyBalance:
    def __init__(self):
        self.balance = defaultdict(lambda: 0)  # self.balance['symbol'] = amt (ex -10)

    def getBalance(self):
        return self.balance

    def updateBalance(self):
        pass

    def awaitUpdateEvent(self):
        pass

    def clearUpdateEvent(self):
        pass


class DummyLogger:
    def __init__(self):
        pass

    def getLogger(self):
        return None
