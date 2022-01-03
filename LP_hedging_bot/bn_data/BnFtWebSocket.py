import asyncio
from binance import AsyncClient, DepthCacheManager, BinanceSocketManager
from binance.enums import FuturesType
import json
from collections import defaultdict
from bn_data.BnCommons import *
from common.SingleTonAsyncInit import SingleTonAsyncInit
from common.createTask import RUNNING_FLAG
from config.config import getConfigKeys


class BnFtWebSocket(SingleTonAsyncInit):
    async def _asyncInit(self, client: AsyncClient, pSymbols):
        self.cli = client
        self.stream = ''
        self.symbolLU = defaultdict(lambda: None)  # [ticker, market]
        self.newSymbols = []
        self.fiats = FIATS
        # self.orderBook['symbol']['ask'] = [['price', 'qty'], ['price', 'qty'], ['price', 'qty'], ...] bid = want to buy, ask = want to sell
        self.orderBookFt = defaultdict(lambda: defaultdict(lambda: [[0, 0]] * MaxOderBookDepth))
        self.pSymbols = pSymbols  # pSymbols = [symbols, updated]
        self._setSymbols(pSymbols[0])
        self.reRun = False

    def setFiatsOrderBook(self):
        for sym in self.fiats:
            self.orderBookFt[sym]['bid'] = [[1, 100000] * MaxOderBookDepth]
            self.orderBookFt[sym]['ask'] = [[1, 100000] * MaxOderBookDepth]
            self.orderBookFt[sym]['event'] = asyncio.Event()
            self.orderBookFt[sym]['event'].set()

    def getOrderBook(self):
        return self.orderBookFt

    def setSymbols(self, symbols):
        self.newSymbols = symbols
        self.reRun = True

    def _setSymbols(self, symbols):
        self.resetSymbols()
        self.setFiatsOrderBook()
        for symbol in symbols:
            self.addStream(symbol, '{}@depth5@100ms')

    def addStream(self, sym: str, ev: str):
        stream = ev.format(sym.lower())
        if len(self.stream) == 0:
            self.stream = stream
        else:
            self.stream = self.stream + '/' + stream
        self.orderBookFt[sym.upper()]['event'] = asyncio.Event()

    def resetSymbols(self):
        self.resetStream()
        self._resetDict()

    def resetStream(self):
        self.stream = ''

    def _resetDict(self):
        keys = list(self.orderBookFt.keys())
        for k in keys:
            del self.orderBookFt[k]

        # self.orderBookFt = defaultdict(lambda: defaultdict(lambda: [[0, 0]] * MaxOderBookDepth))
        # 포인터가 바뀌어 버림

    async def awaitOrderBookUpdate(self):
        books = list(self.orderBookFt.values())
        tasks = [asyncio.create_task(book['event'].wait()) for book in books]
        returns, pending = await asyncio.wait(tasks)

    def clearAwaitEvent(self):
        for sym, book in self.orderBookFt.items():
            if sym not in self.fiats:
                book['event'].clear()

    async def _run(self):
        self.bsm = BinanceSocketManager(self.cli)
        async with self.bsm._get_futures_socket(path=self.stream, futures_type=FuturesType.USD_M) as ts:
            print(self.stream + " is opened")
            while RUNNING_FLAG[0] and not self.reRun and not self.pSymbols[1]:
                msg = await ts.recv()
                etype, symbol = msg['data']['e'], msg['data']['s']

                if etype == 'depthUpdate':
                    self.consumerOrderBook(msg)
                else:
                    print("분류되지 않은 stream (of websocket)", etype, symbol)

        self.clearAwaitEvent()  # 만약 while문 터지면 실행되야함
        self.setSymbols(self.pSymbols[0])

    async def run(self):
        while RUNNING_FLAG[0]:
            await self._run()
            if self.reRun:
                self._setSymbols(self.newSymbols)
                self.reRun = False
                self.pSymbols[1] = False

    def consumerOrderBook(self, msg):
        symbol = msg['data']['s']

        ticker, market = symbolToTickerMarket(symbol)

        for i, b in enumerate(msg['data']['b']):  # buy 삽니다
            self.orderBookFt[symbol]['bid'][i] = b
        for i, a in enumerate(msg['data']['a']):  # sell 팝니다
            self.orderBookFt[symbol]['ask'][i] = a

        self.orderBookFt[symbol]['event'].set()

        # print(ticker, self.orderBook[ticker]['bid'][0]) # debug


async def main():
    configKeys = getConfigKeys()
    client = await AsyncClient.create(configKeys['binance']['api_key'], configKeys['binance']['secret_key'])

    symbols = ['KLAYUSDT', 'XRPUSDT']
    bnFtWebSocket = await BnFtWebSocket.createIns(client, symbols)

    RUNNING_FLAG[0] = True
    await bnFtWebSocket.run()

    print(len('as'))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    print("끝")
