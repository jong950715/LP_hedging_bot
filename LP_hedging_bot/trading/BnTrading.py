import asyncio
from binance import AsyncClient
from bn_data.BnCommons import *
from decimal import Decimal
from bn_data.BnBalance import BnBalance
from bn_data.BnFtWebSocket import BnFtWebSocket
from bn_data.BnSpWebSocket import BnSpWebSocket
from bn_data.BnExInfo import BnExInfo
from trading.enums import VAL_OPTION
from config.config import getConfigKeys
from common.SingleTonAsyncInit import SingleTonAsyncInit
from view.MyLogger import MyLogger
from common.createTask import createTask, RUNNING_FLAG
from common.MyScheduler import MyScheduler


class BnTrading(SingleTonAsyncInit):
    async def _asyncInit(self, client: AsyncClient, pSymbols, myConfig, bnExInfo: BnExInfo,
                         bnBalance: BnBalance, bnFtWebSocket: BnFtWebSocket, bnSpWebSocket: BnSpWebSocket):
        self.pSymbols = pSymbols

        self.configPools = myConfig.getConfig('configPools')
        self.configTrading = myConfig.getConfig('configCommon')['trading']
        self.orderBookFt = bnFtWebSocket.getOrderBook()
        self.orderBookSp = bnSpWebSocket.getOrderBook()
        self.balance = bnBalance.getBalance()
        self.orderInfo = await bnExInfo.getOrderInfo()

        self.cli = client

        self.myConfig = myConfig
        self.bnExInfo = bnExInfo
        self.bnBalance = bnBalance
        self.bnFtWebSocket = bnFtWebSocket
        self.bnSpWebSocket = bnSpWebSocket

        self.targetBalance = defaultdict(lambda: 0)
        self.poolSize = defaultdict(lambda: 0)

        self.fiats = FIATS

        self.logger = MyLogger.getInsSync().getLogger()

        self.exportData = defaultdict(lambda: defaultdict(lambda: 0.0))

        # 메소드 입양 (클래스의 메소드가 아니라 인스턴스의 메소드가 넘어오긴하는데 가독성 측면에서 안티코드는 아닌지 고민필요)
        # 인스턴스 자체를 입양하면 접근성에 대한 보호가 사라져서 제한적으로 가져오고 싶은 마음에 짜인 코드임
        # self.isOrderBookUpdated = bnWebSocket.isOrderBookUpdated
        # self.resetFlagOrderBookUpdate = bnWebSocket.resetFlagOrderBookUpdate

    def getExportData(self):
        return self.exportData

    async def order(self, sym, price, qty):
        # print("order : ", sym, price, qty)
        order = Order(self.cli, self.orderInfo, sym, price, qty)
        await order.execute()

    def calcTargetBalance(self):
        for sym in self.targetBalance.keys():
            self.targetBalance[sym] = 0
            self.poolSize[sym] = 0

        for k, configPool in self.configPools.items():
            sym1 = configPool['sym1']
            sym2 = configPool['sym2']

            targetAmt1 = configPool['sym1_target']
            targetAmt2 = configPool['sym2_target']

            k = configPool['k']

            p1 = (float(self.orderBookSp[sym1]['bid'][0][0]) + float(self.orderBookSp[sym1]['ask'][0][0])) / 2
            p2 = (float(self.orderBookSp[sym2]['bid'][0][0]) + float(self.orderBookSp[sym2]['ask'][0][0])) / 2

            n1 = (k * p2 / p1) ** 0.5
            # n2 = (k * p1 / p2)**0.5
            n2 = k / n1

            if sym1 not in self.fiats:
                self.targetBalance[sym1] += (targetAmt1 - n1)
                self.poolSize[sym1] += n1
            if sym2 not in self.fiats:
                self.targetBalance[sym2] += (targetAmt2 - n2)
                self.poolSize[sym2] += n2

    def getRates(self, sym):
        bidF = float(self.orderBookFt[sym]['bid'][0][0])  # 삽니다.
        askF = float(self.orderBookFt[sym]['ask'][0][0])  # 팝니다.
        spreadF = askF - bidF
        centerPriceF = (bidF + askF) / 2

        bidS = float(self.orderBookSp[sym]['bid'][0][0])  # 삽니다.
        askS = float(self.orderBookSp[sym]['ask'][0][0])  # 팝니다.
        spreadS = askS - bidS
        centerPriceS = (bidS + askS) / 2

        n = self.targetBalance[sym]
        amt = float(self.balance[sym])
        N = self.poolSize[sym]
        triggerRate = (n - amt) / N if N != 0 else 0

        return triggerRate, spreadF / centerPriceF, spreadS / centerPriceS, (centerPriceF / centerPriceS - 1)

    def setExportData(self, sym, triggerRate, spreadRateFt, spreadRateSp, sfDiffRate):
        self.exportData[sym]['triggerRate'] = triggerRate
        self.exportData[sym]['spreadRateFt'] = spreadRateFt
        self.exportData[sym]['spreadRateSp'] = spreadRateSp
        self.exportData[sym]['sfDiffRate'] = sfDiffRate

    def generateOrderList(self):
        orders = []  # 결과물 담을 리스트
        for sym in self.targetBalance.keys():  # symbol 하나씩 순회 하면서 괴리율 점검
            triggerRate, spreadRateFt, spreadRateSp, sfDiffRate = self.getRates(sym)

            self.setExportData(sym, triggerRate, spreadRateFt, spreadRateSp, sfDiffRate)

            if (abs(triggerRate) > self.configTrading['diff_trigger_rate']) and (
                    spreadRateFt < self.configTrading['futures_spread_tol_rate']) and (
                    spreadRateSp < self.configTrading['spot_spread_tol_rate']) and (
                    abs(sfDiffRate) < self.configTrading['spot_futures_diff_tol_rate']):
                n = self.targetBalance[sym]
                amt = float(self.balance[sym])

                if (n - amt) > 0:
                    n = n - self.poolSize[sym] * self.configTrading['diff_trigger_rate'] * \
                        self.configTrading['order_qty_rate']
                    price = Decimal(self.orderBookFt[sym]['bid'][0][0]) + self.orderInfo[sym]['priceStep']
                else:
                    n = n + self.poolSize[sym] * self.configTrading['diff_trigger_rate'] * \
                        self.configTrading['order_qty_rate']
                    price = Decimal(self.orderBookFt[sym]['ask'][0][0]) - self.orderInfo[sym]['priceStep']

                qty = (n - amt)

                orders.append((sym, price, qty))

        return orders

    async def submitOrders(self, orders):
        tasks = [createTask(asyncio.sleep(0))]  # empty tasks
        for o in orders:
            tasks.append(createTask(self.order(*o)))  # o = (sym, price, qty)

        returns, pending = await asyncio.wait(tasks)

    async def cancelAllOrder(self):
        pass

    async def cancelOrders(self, orders):
        tasks = [createTask(asyncio.sleep(0))]  # empty tasks
        for sym, price, qty in orders:
            tasks.append(createTask(self.cli.futures_cancel_all_open_orders(symbol=sym)))

        returns, pending = await asyncio.wait(tasks)

    async def checkPoolUpdate(self):
        if self.myConfig.checkPoolUpdate():
            self.pSymbols[1] = True
            self.pSymbols[2] = True
            await self.bnExInfo.updateOrderFilters()

        while (self.pSymbols[1] == True) or (self.pSymbols[2] == True):
            await asyncio.sleep(0.15)

    async def run(self):
        while RUNNING_FLAG[0]:
            await self.checkPoolUpdate()

            await self.bnBalance.updateBalance()

            await self.bnFtWebSocket.awaitOrderBookUpdate()
            await self.bnSpWebSocket.awaitOrderBookUpdate()
            await self.bnBalance.awaitUpdateEvent()

            self.bnFtWebSocket.clearAwaitEvent()
            self.bnFtWebSocket.clearAwaitEvent()
            self.bnBalance.clearUpdateEvent()

            self.calcTargetBalance()
            orders = self.generateOrderList()

            if orders:
                await self.submitOrders(orders)
                await asyncio.sleep(3)
                await self.cancelOrders(orders)


class Order:
    def __init__(self, client: AsyncClient, orderInfo, sym, price, qty):
        # Do use decimal!
        self.cli = client
        self.orderInfo = orderInfo
        self.sym = sym
        self.price = Decimal(str(price))
        self.qty = Decimal(str(qty))
        self.priceStep = Decimal(self.orderInfo[self.sym]['priceStep'])
        self.qtyStep = Decimal(self.orderInfo[self.sym]['qtyStep'])
        self.minValue = Decimal(self.orderInfo[self.sym]['minValue'])
        self.error = 0x00

    def validate(self):
        # 가격 step, 수량 step, 최소 주문금액, 최소 주문량
        # issue:: 주문금액, 포지션 금액 확인해서 청산비율 체크

        if self.price % self.priceStep != 0:
            message = " =====가격 정밀도 에러===== \n price : " + str(self.price) + "\n priceStep : " + str(
                self.priceStep) + '\n =====가격 정밀도 에러=====\n'
            raise Exception(message)
        if self.qty % self.qtyStep != 0:
            message = (' =====수량 정밀도 에러====='
                       '\n sym : {0}'
                       '\n qty : {1}'
                       '\n qtyStep : {2}'
                       '\n =====수량 정밀도 에러=====\n '
                       .format(self.sym, self.qty, self.qtyStep))
            raise Exception(message)
        if abs(self.qty * self.price) < self.minValue:
            self.error |= 0x01
            if MyScheduler.getInsSync().checkFlags('minValue{0}'.format(self.sym)) is False:
                message = (' =====주문금액 작아서 에러===== '
                           '\n sym : {0} '
                           '\n qty*price : {1} '
                           '\n =====주문금액 작아서 에러=====\n'
                           .format(self.sym, self.qty * self.price))
                MyLogger.getInsSync().getLogger().warning(message)

    def fitByRound(self):
        # 가격 step, 수량 step에 대해 반올림 --> 주문금액, 주문량 나옴
        # 최소 주문금액, 최소 주문량에 대해는 validate
        self.price = self.priceStep * round(self.price / self.priceStep)
        self.qty = self.qtyStep * round(self.qty / self.qtyStep)
        self.validate()

    async def buy(self):
        res = await self.cli.futures_create_order(symbol=self.sym, price=self.price,
                                                  quantity=self.qty, side='BUY',
                                                  type='LIMIT', timeInForce='GTC')
        self.logOrder()

    async def sell(self):
        res = await self.cli.futures_create_order(symbol=self.sym, price=self.price,
                                                  quantity=-self.qty, side='SELL',
                                                  type='LIMIT', timeInForce='GTC')
        self.logOrder()

    def logOrder(self):
        MyLogger.getInsSync().getLogger().debug(
            '#ORDER#'
            '\n sym : %s'
            '\n p : %f'
            '\n q : %f' % (self.sym, self.price, self.qty))

    async def execute(self, valOp: VAL_OPTION = VAL_OPTION.FIT_BY_ROUND):
        # 검증
        if valOp == VAL_OPTION.FIT_BY_ROUND:
            self.fitByRound()
        elif valOp == VAL_OPTION.ASSERT_ERROR:
            self.validate()

        # 실행
        if self.error:
            return

        if self.qty > 0:
            await self.buy()
        elif self.qty < 0:
            await self.sell()
        else:
            raise Exception("qty 0 주문은 안돼~")


async def main():
    client = await AsyncClient.create(api_key, api_secret)
    bnTrading = BnTrading(client=client)

    await bnTrading.order('TRXUSDT', 0.1001, -30.01)

    await client.close_connection()
    return

    param = dict()
    param['symbol'] = 'TRXUSDT'  #
    param['side'] = 'BUY'
    param['type'] = 'LIMIT'
    param['timeInForce'] = 'GTC'
    param['quantity'] = 110
    param['price'] = 0.070
    res = await client.futures_create_order(**param)

    # param = dict()
    # param['symbol'] = 'TRXUSDT'
    # res = await client.futures_cancel_all_open_orders(**param)

    print(client.response.headers)
    print(res)

    await client.close_connection()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
