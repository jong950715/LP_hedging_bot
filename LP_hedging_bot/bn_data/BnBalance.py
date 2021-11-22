import asyncio
from binance import AsyncClient
import json
from collections import defaultdict
from bn_data.BnCommons import *
from common.SingleTonAsyncInit import SingleTonAsyncInit
import time


class BnBalance(SingleTonAsyncInit):
    async def _asyncInit(self, client: AsyncClient, symbols):
        self.cli = client
        self.symbols = []
        self.balance = defaultdict(lambda: 0)  # self.balance['symbol'] = amt (ex -10)
        self.prev = 0
        self.flagUpdated = False
        self.symbols = symbols

    def addSymbol(self, s):
        self.symbols.append(s)

    def setSymbols(self, s):
        self.symbols = s

    def getBalance(self):
        return self.balance

    def setFlagUpdate(self):
        self.flagUpdated = True

    def resetFlagUpdate(self):
        self.flagUpdated = False

    def isUpdated(self):
        if self.flagUpdated is True:
            return True
        else:
            return False

    async def updateBalance(self):
        tasks = [asyncio.create_task(self.cli.futures_position_information(symbol=symbol)) for symbol in
                 self.symbols]
        returns, pending = await asyncio.wait(tasks)
        for ret in returns:
            msg = ret.result()[0]

            sym = msg['symbol']
            tic, market = symbolToTickerMarket(sym)
            amt = msg['positionAmt']
            self.balance[sym] = amt
            # print(sym, tic, amt)

    async def run(self):
        while True:
            await self.updateBalance()
            self.setFlagUpdate()
            await asyncio.sleep(0.08)
            now = time.time()
            # print("balance : " + str(now - self.prev))
            self.prev = now


async def main():
    client = await AsyncClient.create(api_key, api_secret)
    # client.futures_cancel_all_open_orders(symbol='trxusdt')
    # client.futures_cancel_all_open_orders(symbol='')

    time.sleep(1)
    return

    bnBalance = BnBalance(client)
    bnBalance.addSymbol("TRXUSDT")
    bnBalance.addSymbol("BTCUSDT")
    await bnBalance.updateBalance()
    await client.close_connection()
    return

    res = await client.futures_account_balance()
    # print(json.dumps(res, indent=2))
    param = dict()
    symbols = ['TRXUSDT']

    # param['symbol'] = symbol
    # res = await client.futures_position_information(**param)
    # res = await client.futures_position_information(symbol=symbol)

    # loop = asyncio.get_running_loop()

    tasks = [asyncio.create_task(client.futures_position_information(symbol=symbol)) for symbol in symbols]
    fins, un = await asyncio.wait(tasks)
    for fin in fins:
        print(fin.result())

    # print(json.dumps(res, indent=2))
    await client.close_connection()


async def test():
    client = await AsyncClient.create(api_key, api_secret)
    # res = await client.futures_coin_exchange_info()
    res = await  client.futures_position_information(symbol='TRXUSDT', recvWindow=715)
    print(res)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # loop.run_until_complete(test())
