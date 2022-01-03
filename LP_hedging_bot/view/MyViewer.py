from prettytable import PrettyTable
import asyncio
from bn_data.BnBalance import BnBalance
from bn_data.BnFtWebSocket import BnFtWebSocket
from bn_data.BnExInfo import BnExInfo
from bn_data.BnCommons import symbolToTickerMarket
from trading.BnTrading import BnTrading
from view.MyLogger import MyLogger
from common.MyScheduler import MyScheduler
import platform
from common.createTask import RUNNING_FLAG


class MyViewer():
    def __init__(self, myConfig, bnBalance: BnBalance, bnFtWebSocket: BnFtWebSocket, bnTrading: BnTrading, pSymbols):
        self.config = myConfig.getConfig('configCommon')['viewer']
        self.bnFtWebSocket = bnFtWebSocket
        self.bnBalance = bnBalance
        self.balance = bnBalance.getBalance()
        self.orderBookFt = bnFtWebSocket.getOrderBook()
        self.tradingData = bnTrading.getExportData()
        self.pSymbols = pSymbols
        self.tickers = []

        if platform.system() == 'Windows' or platform.system() == 'Darwin':
            self.flagGui = True
        else:
            self.flagGui = False

    def _getTable(self):
        tb = PrettyTable()
        tb.field_names = ['t', 'amt', 'bid', 'trig']

        for sym in self.pSymbols[0]:
            tic, market = symbolToTickerMarket(sym)
            amt = self.balance[sym]
            bid = '${:.3g}'.format(float(self.orderBookFt[sym]['bid'][0][0]))
            triggerRate = '{:.3f}%'.format((self.tradingData[sym]['triggerRate']) * 100)
            tb.add_row([tic, amt, bid, triggerRate])

        return 'LiqPercent: {0:.2f}%\n{1:}'.format(self.bnBalance.getLiqPercent(), tb)

    def checkLiqPercent(self):
        liqPercent = self.bnBalance.getLiqPercent()
        #liqPercent = 79
        if liqPercent < self.config['warning_liq_percent']:
            MyLogger.getInsSync().getLogger().info('liquidation Percent is DANGER!! \n  !! {0}% !!'.format(liqPercent))


    async def run(self):
        await asyncio.sleep(1)

        while RUNNING_FLAG[0]:
            await asyncio.sleep(3)

            self.checkLiqPercent()

            if MyScheduler.getInsSync().checkFlags('runningAlert') is False:
                tb = self._getTable()
                MyLogger.getInsSync().getLogger().info(tb)
