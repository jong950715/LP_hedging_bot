import asyncio
from binance import AsyncClient, DepthCacheManager, BinanceSocketManager
from binance.enums import FuturesType
import json
from collections import defaultdict
from bn_data.BnCommons import *
from common.SingleTonAsyncInit import SingleTonAsyncInit
from config.config import getConfigKeys


class BnSpWebSocket(SingleTonAsyncInit):
    async def _asyncInit(self, client: AsyncClient, symbols):
        self.cli = client
        self.stream = ''
        self.symbolLU = defaultdict(lambda: None)  # [ticker, market]
        self.fiats = FIATS
        # self.orderBook['symbol']['ask'] = [['price', 'qty'], ['price', 'qty'], ['price', 'qty'], ...] bid = want to buy, ask = want to sell
        self.orderBookSp = defaultdict(lambda: defaultdict(lambda: [[0, 0]] * MaxOderBookDepth))
        self.setFiatsOrderBook()
        self.symbols = symbols

    def setFiatsOrderBook(self):
        for sym in self.fiats:
            self.orderBookSp[sym]['bid'] = [[1, 100000] * MaxOderBookDepth]
            self.orderBookSp[sym]['ask'] = [[1, 100000] * MaxOderBookDepth]
            self.orderBookSp[sym]['update'] = True

    def getOrderBook(self):
        return self.orderBookSp

    def addSymbol(self, s):
        self.symbols.append(s)

    def setSymbols(self, s):
        self.symbols = s

    def addStream(self, s: str):
        if len(self.stream) == 0:
            self.stream = s
        else:
            self.stream = self.stream + '/' + s

    def isOrderBookUpdated(self):
        for sym in self.symbols:
            if self.orderBookSp[sym]['update'] is not True:
                return False
        else:
            return True

    def resetFlagOrderBookUpdate(self):
        for sym, book in self.orderBookSp.items():
            book['update'] = False
        for sym in self.fiats:
            self.orderBookSp[sym]['update'] = True

    async def run(self):
        self.bsm = BinanceSocketManager(self.cli)
        async with self.bsm._get_socket(path=self.stream) as ts:
            print(self.stream + " is opened")
            while True:
                msg = await ts.recv()
                self.consumerOrderBook(msg)

    def consumerOrderBook(self, msg):
        symbol = msg['s']

        ticker, market = symbolToTickerMarket(symbol)

        self.orderBookSp[symbol]['bid'][0] = [msg['b'], msg['B']]
        self.orderBookSp[symbol]['ask'][0] = [msg['a'], msg['A']]
        # self.orderBookSp[symbol]['bid'][1][0] += 1 # debug
        self.orderBookSp[symbol]['update'] = True

        #print(symbol, self.orderBookSp[symbol]['bid'][0])  # debug


async def main():
    # initialise the client
    configKeys = getConfigKeys()
    client = await AsyncClient.create(configKeys['binance']['api_key'], configKeys['binance']['secret_key'])

    bsm = await BnSpWebSocket.createIns(client, ['ethusdt', 'btcusdt'])
    bsm.addStream('ethusdt@depth5@500ms')
    bsm.addStream('btcusdt@depth5@500ms')
    await bsm.run()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    print("끝")
