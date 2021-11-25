from trading.BnTrading import BnTrading
from binance import AsyncClient
from bn_data.BnCommons import *
from view.MyConsole import MyConsole
from view.MyTelegram import MyTelegram
from view.MyLogger import MyLogger
from bn_data.BnExInfo import BnExInfo
from bn_data.BnBalance import BnBalance
from bn_data.BnWebSocket import BnWebSocket
from config.config import getConfigKeys, getConfigPools, getConfigTrading
from common.createTask import createTask

import asyncio
import sys
import platform


async def main():
    configPools = getConfigPools()
    configKeys = getConfigKeys()
    configTrading = getConfigTrading()
    symbols = getSymbolsFromPools(configPools)

    # 객체 생성, 의존성 주입
    # layer1
    client = await AsyncClient.create(configKeys['binance']['api_key'], configKeys['binance']['secret_key'])
    myTelegram = await MyTelegram.createIns(configKeys['telegram']['api_key'], configKeys['telegram']['chat_id'])

    # layer1.5
    myLogger = await MyLogger.createIns(myTelegram)  # global

    # layer2
    bnBalance = await BnBalance.createIns(client, symbols)
    bnWebSocket = await BnWebSocket.createIns(client, symbols)
    bnExInfo = await BnExInfo.createIns(client, symbols)

    # layer3
    bnTrading = await BnTrading.createIns(client, configPools=configPools, configTrading=configTrading, bnExInfo=bnExInfo, bnBalance=bnBalance,
                                          bnWebSocket=bnWebSocket)
    myConsole = MyConsole(bnBalance=bnBalance, bnWebSocket=bnWebSocket, symbols=symbols)

    for symbol in symbols:
        bnWebSocket.addStream(symbol.lower() + '@depth5@100ms')  # "ftmusdt@depth5@500ms"

    tasks = []
    try:
        tasks.append(createTask(myTelegram.run()))
        tasks.append(createTask(myLogger.run()))
        tasks.append(createTask(bnWebSocket.run()))
        tasks.append(createTask(bnBalance.run()))
        tasks.append(createTask(bnExInfo.run()))
        if platform.system() == 'Windows' or platform.system() == 'Darwin':
            tasks.append(createTask(myConsole.run()))
        tasks.append(createTask(bnTrading.run()))
        await asyncio.wait(tasks)
    except Exception as e:
        print(e)


def except_hook(cls, exception, traceback):
    # sys.__excepthook__(cls, exception, traceback)
    old_hook(cls, exception, traceback)


if __name__ == "__main__":
    old_hook = sys.excepthook
    sys.excepthook = except_hook
    asyncio.get_event_loop().run_until_complete(main())
