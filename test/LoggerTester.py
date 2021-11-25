from view.MyLogger import MyLogger
from view.MyTelegram import MyTelegram
import asyncio

async def example():
    myTelegram = await MyTelegram.createIns('2126605846:AAErZbnd9wLBEIrzi-r47kjV1H83FlHaKas', 1915409831)
    myLogger = await MyLogger.getIns(myTelegram)

    #MyLogger.getInsSync().setPeriodOfFlagName('flagB', 30)
    MyLogger.getInsSync().setPeriodOfFlagName('flagC', 10)

    tasks = []
    tasks.append(asyncio.create_task(myTelegram.run()))
    tasks.append(asyncio.create_task(myLogger.run()))
    tasks.append(asyncio.create_task(test1()))
    await asyncio.wait(tasks)


async def test1():
    while True:
        if MyLogger.getInsSync().checkFlags('flagA') is False:
            MyLogger.getInsSync().getLogger().warning('flagA_60sec')

        if MyLogger.getInsSync().checkFlags('flagB') is False:
            MyLogger.getInsSync().getLogger().warning('flagB_30sec')

        if MyLogger.getInsSync().checkFlags('flagC') is False:
            MyLogger.getInsSync().getLogger().warning('flagC_10sec')

        await asyncio.sleep(0.01)


if __name__ == '__main__':
    loop_ = asyncio.get_event_loop()
    loop_.run_until_complete(example())