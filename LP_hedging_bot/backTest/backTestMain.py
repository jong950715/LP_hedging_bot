import asyncio
import datetime

from binance import AsyncClient

from backTest.BackTrading import BackTrading
from backTest.DummyClass import DummySocket, DummyBalance, DummyLogger
from backTest.candleData import getPrice
from bn_data.BnCommons import getSymbolsFromPools
from bn_data.BnCommons import *
from bn_data.BnExInfo import BnExInfo
from config.MyConfig import MyConfig
from view.MyLogger import MyLogger


async def main():
    pSymbols = [None, False, False]  # pSymbols = [symbols, Fupdated, Supdated]
    myConfig = await MyConfig.createIns(pSymbols)
    configKeys = myConfig.getConfig('configKeys')
    configPools = myConfig.getConfig('configPools')
    pSymbols[0] = getSymbolsFromPools(configPools)

    client = await AsyncClient.create(configKeys['binance']['api_key'], configKeys['binance']['secret_key'])

    bnExInfo = await BnExInfo.createIns(client, pSymbols)

    MyLogger.chkGetIns=True
    log = MyLogger()
    MyLogger._ins = DummyLogger()

    bnFtWebSocket = DummySocket()
    bnSpWebSocket = bnFtWebSocket
    bnBalance = DummyBalance()

    FIATS.remove('USDT')
    bnTrading = await BackTrading.createIns(client, pSymbols=pSymbols, myConfig=myConfig, bnExInfo=bnExInfo,
                                            bnBalance=bnBalance, bnFtWebSocket=bnFtWebSocket,
                                            bnSpWebSocket=bnSpWebSocket)

    start = int(
        datetime.datetime(2021, 1, 1, 0, 0, 0, 0, datetime.timezone(datetime.timedelta(hours=9))).timestamp()) * 1000
    end = int(
        datetime.datetime(2021, 1, 31, 0, 0, 0, 0, datetime.timezone(datetime.timedelta(hours=9))).timestamp()) * 1000


    inPrice = dict()
    for sym in pSymbols[0]:
        inPrice[sym] = await getPrice(client=client, symbol=sym, start=start, end=end)

    bnTrading.backInit(length=len(inPrice[sym]), inPrice=inPrice, slip=(0.1 / 100))
    print(bnTrading.backRun())
    bnTrading.exportCsv()

    await bnTrading.sweepTest((1/100), (20/100), 10, (0.03/100), (0.1/100), 3)
    bnTrading.exportSweepTest()

    await client.close_connection()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())