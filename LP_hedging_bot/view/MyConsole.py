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


class MyConsole():
    def __init__(self, bnBalance: BnBalance, bnFtWebSocket: BnFtWebSocket, bnTrading: BnTrading, symbols):
        self.bnFtWebSocket = bnFtWebSocket
        self.bnBalance = bnBalance
        self.balance = bnBalance.getBalance()
        self.orderBookFt = bnFtWebSocket.getOrderBook()
        self.tradingData = bnTrading.getExportData()
        self.symbols = symbols
        self.tickers = []

        if platform.system() == 'Windows' or platform.system() == 'Darwin':
            self.flagGui = True
        else:
            self.flagGui = False

    def addSymbol(self, symbol):
        ticker, market = symbolToTickerMarket(symbol)
        self.tickers.append(ticker)
        self.symbols.append(symbol)

    def setSymbols(self, s):
        self.symbols = s

    def _getTable(self):
        tb = PrettyTable()
        tb.field_names = ['t', 'amt', 'bid', 'trig']

        for sym in self.symbols:
            tic, market = symbolToTickerMarket(sym)
            amt = self.balance[sym]
            bid = '${:.3g}'.format(float(self.orderBookFt[sym]['bid'][0][0]))
            triggerRate = '{:.3f}%'.format((self.tradingData[sym]['triggerRate']) * 100)
            tb.add_row([tic, amt, bid, triggerRate])



        return 'LiqPercent: {0:.2f}%\n{1:}'.format(self.bnBalance.getLiqPercent(), tb)

    async def run(self):
        while True:
            await asyncio.sleep(2)

            tb = self._getTable()

            if MyScheduler.getInsSync().checkFlags('runningAlert') is False:
                MyLogger.getInsSync().getLogger().info(tb)
