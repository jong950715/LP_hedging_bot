import asyncio
import datetime
from binance import AsyncClient

from config.MyConfig import MyConfig


async def test():
    pSymbols = [None, False, False]  # pSymbols = [symbols, Fupdated, Supdated]
    myConfig = await MyConfig.createIns(pSymbols)
    configKeys = myConfig.getConfig('configKeys')
    client = await AsyncClient.create(configKeys['binance']['api_key'], configKeys['binance']['secret_key'])
    # 연, 월, 일, 시, 분, 초, 마이크로초, 시간대
    start = int(
        datetime.datetime(2022, 3, 29, 0, 0, 0, 0, datetime.timezone(datetime.timedelta(hours=9))).timestamp()) * 1000
    end = int(
        datetime.datetime(2022, 3, 30, 0, 0, 0, 0, datetime.timezone(datetime.timedelta(hours=9))).timestamp()) * 1000
    interval = 60 * 1000

    onetimeMax = 1000

    res = []

    start -= start % interval
    end -= end % interval
    offset = (((end - start) // interval) % onetimeMax)

    print(start, '\t', offset)
    r = await client._klines(interval='1m', symbol="BTCUSDT", startTime=start, limit=offset)
    res.extend(r)
    start += offset * interval
    while start < end:
        print(start, "\t", onetimeMax)
        r = await client._klines(interval='1m', symbol="BTCUSDT", startTime=start, limit=onetimeMax)
        res.extend(r)
        start += interval * onetimeMax

    rres = [None] * (len(res) * 4)
    for i, x in enumerate(res):
        for j in range(4):
            rres[i * 4 + j] = x[1 + j]

    return rres


async def getPrice(client, symbol, start, end):


    interval = 60 * 1000
    onetimeMax = 1000

    res = []

    start -= start % interval
    end -= end % interval
    offset = (((end - start) // interval) % onetimeMax)

    print(start, '\t', offset)
    r = await client._klines(interval='1m', symbol=symbol, startTime=start, limit=offset)
    res.extend(r)
    start += offset * interval
    while start < end:
        r = await client._klines(interval='1m', symbol=symbol, startTime=start, limit=onetimeMax)
        res.extend(r)
        start += interval * onetimeMax

    rres = [None] * (len(res) * 4)
    for i, x in enumerate(res):
        for j in range(4):
            rres[i * 4 + j] = x[1 + j]

    return rres


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test())
