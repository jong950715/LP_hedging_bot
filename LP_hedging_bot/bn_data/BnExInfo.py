from collections import defaultdict
import asyncio
from common.SingleTonAsyncInit import SingleTonAsyncInit
from binance import AsyncClient
from common.createTask import RUNNING_FLAG
from common.MyScheduler import MyScheduler
from decimal import Decimal


class BnExInfo(SingleTonAsyncInit):
    async def _asyncInit(self, cli: AsyncClient, pSymbols):
        self.cli = cli
        self.orderInfo = defaultdict(dict)
        self.pSymbols = pSymbols
        await asyncio.sleep(0)

    async def getOrderInfo(self):
        await self.updateOrderFilters()
        return self.orderInfo

    async def updateOrderFilters(self):
        msg = await self.cli.futures_exchange_info()
        for x in msg['symbols']:
            sym = x['symbol']
            if sym not in self.pSymbols[0]:
                continue
            for fil in x['filters']:
                if fil['filterType'] == 'PRICE_FILTER':  # 'PRICE_FILTER' 'LOT_SIZE' 'MIN_NOTIONAL'
                    self.orderInfo[sym]['minPrice'] = Decimal(fil['minPrice'])
                    self.orderInfo[sym]['maxPrice'] = Decimal(fil['maxPrice'])
                    self.orderInfo[sym]['priceStep'] = Decimal(fil['tickSize'])
                if fil['filterType'] == 'LOT_SIZE':
                    self.orderInfo[sym]['minQty'] = Decimal(fil['minQty'])
                    self.orderInfo[sym]['maxQty'] = Decimal(fil['maxQty'])
                    self.orderInfo[sym]['qtyStep'] = Decimal(fil['stepSize'])
                if fil['filterType'] == 'MIN_NOTIONAL':
                    self.orderInfo[sym]['minValue'] = Decimal(fil['notional'])

    async def run(self):
        while RUNNING_FLAG[0]:
            if MyScheduler.getInsSync().checkFlags('exInfo') is False:
                await self.updateOrderFilters()
            await asyncio.sleep(10)
