import asyncio
from binance import AsyncClient, DepthCacheManager, BinanceSocketManager
from binance.enums import FuturesType
import json
from collections import defaultdict
from bn_data.BnCommons import *
from common.SingleTonAsyncInit import SingleTonAsyncInit
from common.createTask import RUNNING_FLAG


class BnFtWebSocket(SingleTonAsyncInit):
    async def _asyncInit(self, client: AsyncClient, symbols):
        self.cli = client
        self.stream = ''
        self.symbolLU = defaultdict(lambda: None)  # [ticker, market]
        self.symbols = []
        self.fiats = FIATS
        # self.orderBook['symbol']['ask'] = [['price', 'qty'], ['price', 'qty'], ['price', 'qty'], ...] bid = want to buy, ask = want to sell
        self.orderBookFt = defaultdict(lambda: defaultdict(lambda: [[0, 0]] * MaxOderBookDepth))
        self.setFiatsOrderBook()
        self.symbols = symbols

    def setFiatsOrderBook(self):
        for sym in self.fiats:
            self.orderBookFt[sym]['bid'] = [[1, 100000] * MaxOderBookDepth]
            self.orderBookFt[sym]['ask'] = [[1, 100000] * MaxOderBookDepth]
            self.orderBookFt[sym]['update'] = True
    def getOrderBook(self):
        return self.orderBookFt

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
            if self.orderBookFt[sym]['update'] is not True:
                return False
        else:
            return True

    def resetFlagOrderBookUpdate(self):
        for sym, book in self.orderBookFt.items():
            book['update'] = False
        for sym in self.fiats:
            self.orderBookFt[sym]['update'] = True

    async def run(self):
        self.bsm = BinanceSocketManager(self.cli)
        async with self.bsm._get_futures_socket(path=self.stream, futures_type=FuturesType.USD_M) as ts:
            print(self.stream + " is opened")
            while RUNNING_FLAG[0]:
                msg = await ts.recv()
                etype, symbol = msg['data']['e'], msg['data']['s']

                if etype == 'depthUpdate':
                    self.consumerOrderBook(msg)
                else:
                    print("분류되지 않은 stream (of websocket)", etype, symbol)

    def consumerOrderBook(self, msg):
        symbol = msg['data']['s']

        ticker, market = symbolToTickerMarket(symbol)

        for i, b in enumerate(msg['data']['b']):  # buy 삽니다
            self.orderBookFt[symbol]['bid'][i] = b
        for i, a in enumerate(msg['data']['a']):  # sell 팝니다
            self.orderBookFt[symbol]['ask'][i] = a

        self.orderBookFt[symbol]['update'] = True

        #print(ticker, self.orderBook[ticker]['bid'][0]) # debug


async def main():
    # initialise the client
    client = await AsyncClient.create(api_key, api_secret, tld='com')
    # client = await AsyncClient.create(tld='com')
    bsm = BnFtWebSocket(client)
    bsm.addStream('ethusdt@depth5@500ms')
    bsm.addStream('btcusdt@depth5@500ms')
    await bsm.run()
    print(len('as'))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    print("끝")
