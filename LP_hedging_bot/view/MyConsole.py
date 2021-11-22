from prettytable import PrettyTable
import asyncio
from bn_data.BnBalance import BnBalance
from bn_data.BnWebSocket import BnWebSocket
from bn_data.BnExInfo import BnExInfo
from bn_data.BnCommons import symbolToTickerMarket


class MyConsole():
    def __init__(self, bnBalance: BnBalance, bnWebSocket: BnWebSocket, symbols):
        self.bnWebSocket = bnWebSocket
        self.bnBalance = bnBalance
        self.balance = bnBalance.getBalance()
        self.orderBook = bnWebSocket.getOrderBook()
        self.symbols = symbols
        self.tickers = []

    async def run(self):
        while True:
            await asyncio.sleep(1)
            print('\n\n\n\n', flush=False)
            tb = PrettyTable()
            tb.field_names = ['ticker', 'amt', 'bid', 'ask']

            for sym in self.symbols:
                amt = self.balance[sym]
                bid = self.orderBook[sym]['bid'][0][0]
                ask = self.orderBook[sym]['ask'][0][0]
                tb.add_row([sym, amt, bid, ask])

            print(tb, flush=False)
            print('\n')

    def addSymbol(self, symbol):
        ticker, market = symbolToTickerMarket(symbol)
        self.tickers.append(ticker)
        self.symbols.append(symbol)

    def setSymbols(self, s):
        self.symbols = s
