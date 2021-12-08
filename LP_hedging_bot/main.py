from trading.BnTrading import BnTrading
from binance import AsyncClient
from bn_data.BnCommons import *
from view.MyConsole import MyConsole
from view.MyTelegram import MyTelegram
from view.MyLogger import MyLogger
from bn_data.BnExInfo import BnExInfo
from bn_data.BnBalance import BnBalance
from bn_data.BnFtWebSocket import BnFtWebSocket
from bn_data.BnSpWebSocket import BnSpWebSocket
from config.config import getConfigKeys, getConfigPools, getConfigTrading, getConfigLogger, getConfigScheduler
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
    myConfig = await MyConfig.createIns()
    configPools = myConfig.getConfig('configPools')
    configKeys = myConfig.getConfig('configKeys')
    configTrading = myConfig.getConfig('configTrading')
    configLogger = myConfig.getConfig('configLogger')
    configScheduler = myConfig.getConfig('configScheduler')
    symbols = getSymbolsFromPools(configPools)

    # 객체 생성, 의존성 주입

    # layer0.5
    myScheduler = await MyScheduler.createIns(configScheduler)  # 직접 주입하지는 않고 알아서 가져다 쓰는걸로

    # layer1
    client = await AsyncClient.create(configKeys['binance']['api_key'], configKeys['binance']['secret_key'])
    myTelegram = await MyTelegram.createIns(configKeys['telegram']['api_key'], configKeys['telegram']['chat_id']
                                            , myConfig)

    # layer1.5
    myLogger = await MyLogger.createIns(myTelegram, configLogger)  # 직접 주입하지는 않고 알아서 가져다 쓰는걸로

    # layer2
    bnBalance = await BnBalance.createIns(client, symbols)
    bnFtWebSocket = await BnFtWebSocket.createIns(client, symbols)
    bnSpWebSocket = await BnSpWebSocket.createIns(client, symbols)
    bnExInfo = await BnExInfo.createIns(client, symbols)

    # layer3
    bnTrading = await BnTrading.createIns(client, configPools=configPools, configTrading=configTrading,
                                          bnExInfo=bnExInfo, bnBalance=bnBalance, bnFtWebSocket=bnFtWebSocket,
                                          bnSpWebSocket=bnSpWebSocket)

    # layer4
    myConsole = MyConsole(bnBalance=bnBalance, bnFtWebSocket=bnFtWebSocket, bnTrading=bnTrading, symbols=symbols)
    if flagGui:
        from view.MyMonitor import MyMonitor
        myMonitor = await MyMonitor.createIns(bnBalance=bnBalance, bnFtWebSocket=bnFtWebSocket,
                                              bnSpWebSocket=bnSpWebSocket, bnTrading=bnTrading, symbols=symbols,
                                              flagGui=flagGui)

    for symbol in symbols:
        bnFtWebSocket.addStream(symbol.lower() + '@depth5@100ms')  # "ftmusdt@depth5@500ms"
        bnSpWebSocket.addStream(symbol.lower() + '@bookTicker')  # "ftmusdt@depth5@500ms"

    myLogger.getLogger().error("start")

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

        tasks.append(createTask(myConsole.run()))
        if flagGui:
            tasks.append(createTask(myMonitor.run()))
        await asyncio.wait(tasks)
    except Exception as e:
        print(e)
        raise e
    finally:
        client.close_connection()


def delete_ins(ins):
    referrers = gc.get_referrers(ins)
    for referrer in referrers:
        if type(referrer) == dict:
            for key, value in referrer.items():
                if value is ins:
                    referrer[key] = None


def resetSingleTon():
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        flagGui = True
    else:
        flagGui = False
    delete_ins(MyConfig.getInsSync())
    delete_ins(MyScheduler.getInsSync())
    delete_ins(MyTelegram.getInsSync())
    delete_ins(MyLogger.getInsSync())
    delete_ins(BnBalance.getInsSync())
    delete_ins(BnFtWebSocket.getInsSync())
    delete_ins(BnSpWebSocket.getInsSync())
    delete_ins(BnExInfo.getInsSync())
    delete_ins(BnTrading.getInsSync())
    if flagGui:
        from view.MyMonitor import MyMonitor
        delete_ins(MyMonitor.getInsSync())

    MyConfig.selfDestruct()
    #
    # _ins = None
    # chkGetIns = False
    MyScheduler.selfDestruct()
    MyTelegram.selfDestruct()
    MyLogger.selfDestruct()

    # layer2
    BnBalance.selfDestruct()
    BnFtWebSocket.selfDestruct()
    BnSpWebSocket.selfDestruct()
    BnExInfo.selfDestruct()

    # layer3
    BnTrading.selfDestruct()
    if flagGui:
        from view.MyMonitor import MyMonitor
        MyMonitor.selfDestruct()


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
