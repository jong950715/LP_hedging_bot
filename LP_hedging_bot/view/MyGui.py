import tkinter.ttk
from common.SingleTonAsyncInit import SingleTonAsyncInit
import asyncio
from collections import defaultdict
from bn_data.BnWebSocket import BnWebSocket
from bn_data.BnBalance import BnBalance
from trading.BnTrading import BnTrading


class MyGui(SingleTonAsyncInit):
    async def _asyncInit(self, bnBalance: BnBalance,
                         bnWebSocket: BnWebSocket,
                         bnTrading: BnTrading, symbols):
        self.symbols = symbols
        self.orderBook = bnWebSocket.getOrderBook()
        self.balance = bnBalance.getBalance()
        self.tradingData = bnTrading.getExportData()

        self.bnBalance = bnBalance

        self.root = tkinter.Tk()
        self.root.title('AutoHedgingBot')

        self.treeViews = dict()
        self.treeLists = defaultdict(lambda: [[]])
        self._initTreeView()

    def updateTreeView(self):
        for name, treeView in self.treeViews.items():
            self._updateTreeView(treeView, self.treeLists[name])

    def _updateTreeView(self, treeView, treeList):
        lenView = len(treeView.get_children())
        lenData = len(treeList)
        if lenView < lenData:
            for i in range(lenView, lenData):
                treeView.insert('', i, iid=i)
        elif lenView > lenData:
            for i in range(lenData, lenView):
                treeView.delete(i)
        elif lenView == lenData:
            pass

        for i in range(len(treeView.get_children())):
            treeView.item(item=i, values=treeList[i])

    def _initTreeView(self):
        self.treeViews['common'] = self.newTreeViewByCols(['liquidation'])
        self.treeViews['sym'] = self.newTreeViewByCols(['sym', 'price', 'amt', 'diff', 'spread'])

    def newTreeViewByCols(self, cols):
        treeView = tkinter.ttk.Treeview(self.root, columns=cols, show='headings')
        treeView.pack()

        for col in cols:
            treeView.column(col, width=100, anchor="center")
            treeView.heading(col, text=col, anchor="center")

        return treeView

    def _runSymTreeView(self):
        tL = [[0 for _ in range(5)] for _ in range(len(self.symbols))]
        for i, sym in enumerate(self.symbols):
            tL[i][0] = sym
            tL[i][1] = self.orderBook[sym]['bid'][0][0]
            tL[i][2] = self.balance[sym]
            tL[i][3] = '{:.3f}%'.format((self.tradingData[sym]['diffRate']-1)*100)
            tL[i][4] = '{:.3f}%'.format(self.tradingData[sym]['spreadRate']*100)

        self.treeLists['sym'] = tL
        self.treeLists['common'] = [[self.bnBalance.getLiqPercent()]]

    async def run(self):
        while True:
            await asyncio.sleep(1)
            self._runSymTreeView()
            self.updateTreeView()
            self.root.update()
