import asyncio

#from aiohttp import ClientOSError
import aiohttp
from binance import AsyncClient
import json
from collections import defaultdict
import traceback

from view.MyLogger import MyLogger
from binance.exceptions import BinanceRequestException, BinanceAPIException

from bn_data.BnCommons import *
from common.SingleTonAsyncInit import SingleTonAsyncInit
from config.config import getConfigKeys
from common.safeDivide import safeDivide
from common.createTask import createTask, RUNNING_FLAG
import time


class BnBalance(SingleTonAsyncInit):
    async def _asyncInit(self, client: AsyncClient, symbols):
        self.cli = client
        self.symbols = []
        self.balance = defaultdict(lambda: 0)  # self.balance['symbol'] = amt (ex -10)
        self.prev = 0
        self.updateEvent = asyncio.Event()
        self.symbols = symbols
        self.liqPercent = 0

    def addSymbol(self, s):
        self.symbols.append(s)

    def setSymbols(self, s):
        self.symbols = s

    def getBalance(self):
        return self.balance

    def setUpdateEvent(self):
        self.updateEvent.set()

    def clearUpdateEvent(self):
        self.updateEvent.clear()

    async def awaitUpdateEvent(self):
        await self.updateEvent.wait()

    async def _updateBalance(self):
        # tasks = [asyncio.create_task(self.cli.futures_position_information(symbol=symbol)) for symbol in self.symbols]
        tasks = [asyncio.create_task(self.cli.futures_position_information(symbol=symbol)) for symbol in self.symbols]
        returns, pending = await asyncio.wait(tasks)
        netSum = 0.0
        notionalSum = 0.0
        for ret in returns:
            try:
                await ret
            except Exception as e:
                raise e
            msg = ret.result()[0]

            sym = msg['symbol']
            amt = msg['positionAmt']
            self.balance[sym] = amt

            # 담보비율
            liqP = float(msg['liquidationPrice'])
            mkP = float(msg['markPrice'])
            notional = float(msg['notional'])
            try:
                netSum += (liqP / mkP - 1) * notional
            except ZeroDivisionError as e:
                netSum += 0
            notionalSum += notional

        self.liqPercent = safeDivide(safeDivide(netSum, notionalSum), len(returns)) * 100
        self.setUpdateEvent()

    async def updateBalance(self):
        try:
            await self._updateBalance()
        except (BinanceRequestException, BinanceAPIException, aiohttp.ClientOSError, asyncio.exceptions.TimeoutError) as e:
            emsg = traceback.format_exc()
            MyLogger.getInsSync().getLogger().warning(emsg)
            await self.updateBalance()
        except Exception as e:
            raise e

    def getLiqPercent(self):
        return self.liqPercent

    async def run(self):
        while RUNNING_FLAG[0]:
            await self.updateBalance()
            await asyncio.sleep(10)


async def main():
    configKeys = getConfigKeys()
    client = await AsyncClient.create(configKeys['binance']['api_key'], configKeys['binance']['secret_key'])

    res0 = await client.get_exchange_info()
    print(res0)
    return
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
    # get_exchange_info


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # loop.run_until_complete(prac())
