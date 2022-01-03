import asyncio
from binance import AsyncClient, DepthCacheManager, BinanceSocketManager
from binance.enums import FuturesType
import json
from collections import defaultdict
from bn_data.BnCommons import *
from common.SingleTonAsyncInit import SingleTonAsyncInit
from config.config import getConfigKeys
from common.createTask import RUNNING_FLAG


class BnSpWebSocket(SingleTonAsyncInit):
    async def _asyncInit(self, client: AsyncClient, pSymbols):
        self.cli = client
        self.stream = ''
        self.symbolLU = defaultdict(lambda: None)  # [ticker, market]
        self.newSymbols = []
        self.fiats = FIATS
        # self.orderBook['symbol']['ask'] = [['price', 'qty'], ['price', 'qty'], ['price', 'qty'], ...] bid = want to buy, ask = want to sell
        self.orderBookSp = defaultdict(lambda: defaultdict(lambda: [[0, 0]] * MaxOderBookDepth))
        self.pSymbols = pSymbols  # pSymbols = [symbols, updated]
        self._setSymbols(pSymbols[0])
        self.reRun = False

    def setFiatsOrderBook(self):
        for sym in self.fiats:
            self.orderBookSp[sym]['bid'] = [[1, 100000] * MaxOderBookDepth]
            self.orderBookSp[sym]['ask'] = [[1, 100000] * MaxOderBookDepth]
            self.orderBookSp[sym]['event'] = asyncio.Event()
            self.orderBookSp[sym]['event'].set()

    def getOrderBook(self):
        return self.orderBookSp

    def setSymbols(self, symbols):
        self.newSymbols = symbols
        self.reRun = True

    def _setSymbols(self, symbols):
        self.resetSymbols()
        self.setFiatsOrderBook()
        for symbol in symbols:
            self.addStream(symbol, '{}@bookTicker')

    def addStream(self, sym: str, ev: str):
        stream = ev.format(sym.lower())
        if len(self.stream) == 0:
            self.stream = stream
        else:
            self.stream = self.stream + '/' + stream
        self.orderBookSp[sym.upper()]['event'] = asyncio.Event()

    def resetSymbols(self):
        self.resetStream()
        self._resetDict()

    def resetStream(self):
        self.stream = ''

    def _resetDict(self):
        keys = list(self.orderBookSp.keys())
        for k in keys:
            del self.orderBookSp[k]

        # self.orderBookSp = defaultdict(lambda: defaultdict(lambda: [[0, 0]] * MaxOderBookDepth))
        # 포인터가 바뀌어 버림

    async def awaitOrderBookUpdate(self):
        books = list(self.orderBookSp.values())
        tasks = [asyncio.create_task(book['event'].wait()) for book in books]
        returns, pending = await asyncio.wait(tasks)

    def clearAwaitEvent(self):
        for sym, book in self.orderBookSp.items():
            if sym not in self.fiats:
                book['event'].clear()

    async def _run(self):
        self.bsm = BinanceSocketManager(self.cli)
        async with self.bsm._get_socket(path=self.stream) as ts:
            print(self.stream + " is opened")
            while RUNNING_FLAG[0] and not self.reRun and not self.pSymbols[2]:
                msg = await ts.recv()
                self.consumerOrderBook(msg)
            self.clearAwaitEvent()  # 만약 while문 터지면 실행되야함
            self.setSymbols(self.pSymbols[0])

    async def run(self):
        while RUNNING_FLAG[0]:
            await self._run()
            if self.reRun:
                self._setSymbols(self.newSymbols)
                self.reRun = False
                self.pSymbols[2] = False



    def consumerOrderBook(self, msg):
        symbol = msg['s']

        ticker, market = symbolToTickerMarket(symbol)

        self.orderBookSp[symbol]['bid'][0] = [msg['b'], msg['B']]
        self.orderBookSp[symbol]['ask'][0] = [msg['a'], msg['A']]

        self.orderBookSp[symbol]['event'].set()

        # print(symbol, self.orderBookSp[symbol]['bid'][0])  # debug


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
