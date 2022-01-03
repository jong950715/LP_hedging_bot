from trading.BnTrading import Order
from binance import AsyncClient
import asyncio
from config.config import getConfigKeys
from bn_data.BnExInfo import BnExInfo


async def orderTest():
    # given
    configBinance = getConfigKeys()
    client = await AsyncClient.create(configBinance['binance']['api_key'], configBinance['binance']['secret_key'])

    bnExInfo = await BnExInfo.createIns(client)
    #bnExInfo.setSymbols(['TRXUSDT'])
    orderInfo = await bnExInfo.getOrderInfo()

    # when
    sym, price, qty = 'TRXUSDT', 0.001, 10
    order = Order(client, orderInfo, sym, price, qty)
    await order.execute()
    await client.close_connection()

    # then


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orderTest())
