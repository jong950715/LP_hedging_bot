from collections import defaultdict
import asyncio
from common.SingleTonAsyncInit import SingleTonAsyncInit
from binance import AsyncClient


class BnExInfo(SingleTonAsyncInit):
    async def _asyncInit(self, cli: AsyncClient, symbols):
        self.cli = cli
        self.symbols = []
        self.orderInfo = defaultdict(dict)
        self.symbols = symbols
        await asyncio.sleep(0)

    async def getOrderInfo(self):
        await self.updateOrderFilters()
        return self.orderInfo

    def setSymbols(self, s):
        self.symbols = s

    async def updateOrderFilters(self):
        msg = await self.cli.futures_exchange_info()
        for x in msg['symbols']:
            sym = x['symbol']
            if sym not in self.symbols:
                continue
            for fil in x['filters']:
                if fil['filterType'] == 'PRICE_FILTER':  # 'PRICE_FILTER' 'LOT_SIZE' 'MIN_NOTIONAL'
                    self.orderInfo[sym]['minPrice'] = fil['minPrice']
                    self.orderInfo[sym]['maxPrice'] = fil['maxPrice']
                    self.orderInfo[sym]['priceStep'] = fil['tickSize']
                if fil['filterType'] == 'LOT_SIZE':
                    self.orderInfo[sym]['minQty'] = fil['minQty']
                    self.orderInfo[sym]['maxQty'] = fil['maxQty']
                    self.orderInfo[sym]['qtyStep'] = fil['stepSize']
                if fil['filterType'] == 'MIN_NOTIONAL':
                    self.orderInfo[sym]['minValue'] = fil['notional']

    async def run(self):
        while True:
            await self.updateOrderFilters()
            await asyncio.sleep(3600)
