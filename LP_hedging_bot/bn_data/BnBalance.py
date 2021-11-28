import asyncio
from binance import AsyncClient
import json
from collections import defaultdict
from bn_data.BnCommons import *
from common.SingleTonAsyncInit import SingleTonAsyncInit
from config.config import getConfigKeys
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
    configKeys = getConfigKeys()
    client = await AsyncClient.create(configKeys['binance']['api_key'], configKeys['binance']['secret_key'])
    res1 = await client.futures_position_information()
    print(res1)
    res2 = await client.futures_position_information(symbol='trxusdt')
    print(res2)
    res3 = await client.futures_account()
    print(res3)
    res4 = await client.futures_account_balance()
    print(res4)
    res5 = await client.futures_leverage_bracket()
    print(res5)

    await client.close_connection()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # loop.run_until_complete(test())
