from prettytable import PrettyTable
import asyncio
from bn_data.BnBalance import BnBalance
from bn_data.BnFtWebSocket import BnFtWebSocket
from bn_data.BnExInfo import BnExInfo
from bn_data.BnCommons import symbolToTickerMarket


class MyConsole():
    def __init__(self, bnBalance: BnBalance, bnFtWebSocket: BnFtWebSocket, symbols):
        self.bnFtWebSocket = bnFtWebSocket
        self.bnBalance = bnBalance
        self.balance = bnBalance.getBalance()
        self.orderBookFt = bnFtWebSocket.getOrderBook()
        self.symbols = symbols
        self.tickers = []

    async def run(self):
        while True:
            await asyncio.sleep(2)
            print('\n\n\n\n', flush=False)
            tb = PrettyTable()
            tb.field_names = ['ticker', 'amt', 'bid', 'ask']

            for sym in self.symbols:
                amt = self.balance[sym]
                bid = self.orderBookFt[sym]['bid'][0][0]
                ask = self.orderBookFt[sym]['ask'][0][0]
                tb.add_row([sym, amt, bid, ask])

            print(tb, flush=False)
            print('\n')

    def addSymbol(self, symbol):
        ticker, market = symbolToTickerMarket(symbol)
        self.tickers.append(ticker)
        self.symbols.append(symbol)

    def setSymbols(self, s):
        self.symbols = s
