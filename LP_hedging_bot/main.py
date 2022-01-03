from trading.BnTrading import BnTrading
from binance import AsyncClient
from bn_data.BnCommons import *
from view.MyViewer import MyViewer
from view.MyTelegram import MyTelegram
from view.MyLogger import MyLogger
from bn_data.BnExInfo import BnExInfo
from bn_data.BnBalance import BnBalance
from bn_data.BnFtWebSocket import BnFtWebSocket
from bn_data.BnSpWebSocket import BnSpWebSocket
from common.createTask import createTask, RUNNING_FLAG
from common.MyScheduler import MyScheduler
from config.MyConfig import MyConfig
import asyncio
import sys
import os
import platform
import gc


async def _main():
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        flagGui = True
    else:
        flagGui = False

    # layer 0
    pSymbols = [None, False, False]  # pSymbols = [symbols, Fupdated, Supdated]
    myConfig = await MyConfig.createIns(pSymbols)
    configPools = myConfig.getConfig('configPools')
    configKeys = myConfig.getConfig('configKeys')
    pSymbols[0] = getSymbolsFromPools(configPools)

    # 객체 생성, 의존성 주입

    # layer0.5
    myScheduler = await MyScheduler.createIns(myConfig)  # 직접 주입하지는 않고 알아서 가져다 쓰는걸로

    # layer1
    client = await AsyncClient.create(configKeys['binance']['api_key'], configKeys['binance']['secret_key'])
    myTelegram = await MyTelegram.createIns(configKeys['telegram']['api_key'], configKeys['telegram']['chat_id'], myConfig)

    # layer1.5
    myLogger = await MyLogger.createIns(myTelegram, myConfig)  # 직접 주입하지는 않고 알아서 가져다 쓰는걸로

    # layer2
    bnBalance = await BnBalance.createIns(client, pSymbols)
    bnFtWebSocket = await BnFtWebSocket.createIns(client, pSymbols)
    bnSpWebSocket = await BnSpWebSocket.createIns(client, pSymbols)
    bnExInfo = await BnExInfo.createIns(client, pSymbols)

    # layer3
    bnTrading = await BnTrading.createIns(client, pSymbols=pSymbols, myConfig=myConfig, bnExInfo=bnExInfo, bnBalance=bnBalance, bnFtWebSocket=bnFtWebSocket, bnSpWebSocket=bnSpWebSocket)

    # layer4
    myViewer = MyViewer(myConfig=myConfig, bnBalance=bnBalance, bnFtWebSocket=bnFtWebSocket, bnTrading=bnTrading, pSymbols=pSymbols)
    if flagGui:
        from view.MyMonitor import MyMonitor
        myMonitor = await MyMonitor.createIns(bnBalance=bnBalance, bnFtWebSocket=bnFtWebSocket,
                                              bnSpWebSocket=bnSpWebSocket, bnTrading=bnTrading, pSymbols=pSymbols,
                                              flagGui=flagGui)


    myLogger.getLogger().info("start")

    tasks = []
    try:
        tasks.append(createTask(myScheduler.run()))
        tasks.append(createTask(myTelegram.run()))
        tasks.append(createTask(myLogger.run()))

        tasks.append(createTask(bnBalance.run()))
        tasks.append(createTask(bnFtWebSocket.run()))
        tasks.append(createTask(bnSpWebSocket.run()))
        tasks.append(createTask(bnExInfo.run()))

        tasks.append(createTask(bnTrading.run()))

        tasks.append(createTask(myViewer.run()))
        if flagGui:
            tasks.append(createTask(myMonitor.run()))
        await asyncio.wait(tasks)
    except Exception as e:
        print(e)
        raise e
    finally:
        client.close_connection()


async def main():
    RUNNING_FLAG[0] = True
    await _main()
    print("reset?")
    # resetSingleTon()
    # gc.collect(generation=2)
    # os.execv(sys.argv[0], sys.argv)
    # os.execl(sys.executable, sys.executable, *sys.argv)
    # gc.get_referents()


def except_hook(cls, exception, traceback):
    # sys.__excepthook__(cls, exception, traceback)
    old_hook(cls, exception, traceback)


if __name__ == "__main__":
    old_hook = sys.excepthook
    sys.excepthook = except_hook
    asyncio.get_event_loop().run_until_complete(main())
