import tkinter.ttk
from common.SingleTonAsyncInit import SingleTonAsyncInit
import asyncio
from collections import defaultdict
from bn_data.BnFtWebSocket import BnFtWebSocket
from bn_data.BnBalance import BnBalance
from trading.BnTrading import BnTrading
from common.createTask import RUNNING_FLAG


class MyMonitor(SingleTonAsyncInit):
    async def _asyncInit(self, bnBalance: BnBalance,
                         bnFtWebSocket: BnFtWebSocket,
                         bnSpWebSocket,
                         bnTrading: BnTrading, pSymbols, flagGui):
        self.pSymbols = pSymbols
        self.flagGui = flagGui
        self.orderBookFt = bnFtWebSocket.getOrderBook()
        self.orderBookSp = bnSpWebSocket.getOrderBook()
        self.balance = bnBalance.getBalance()
        self.tradingData = bnTrading.getExportData()

        self.bnBalance = bnBalance

        if self.flagGui:
            self._initGui()

    def _initGui(self): # GUI
        self.root = tkinter.Tk()
        self.root.title('AutoHedgingBot')
        self.treeViews = dict()
        self.treeLists = defaultdict(lambda: [[]])
        self._initTreeView()

    def updateTreeView(self): # GUI
        for name, treeView in self.treeViews.items():
            self._updateTreeView(treeView, self.treeLists[name])

    def _updateTreeView(self, treeView, treeList): # GUI
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
        self.treeViews['sym'] = self.newTreeViewByCols(
            ['sym', 'price', 'amt', 'trigger', 'spreadF', 'spreadS', 'diffSF'])

    def newTreeViewByCols(self, cols):
        treeView = tkinter.ttk.Treeview(self.root, columns=cols, show='headings')
        treeView.pack()

        for col in cols:
            treeView.column(col, width=100, anchor="center")
            treeView.heading(col, text=col, anchor="center")

        return treeView

    def _runSymTreeView(self):
        tL = [[0 for _ in range(7)] for _ in range(len(self.pSymbols[0]))]
        for i, sym in enumerate(self.pSymbols[0]):
            tL[i][0] = sym
            tL[i][1] = self.orderBookFt[sym]['bid'][0][0]
            tL[i][2] = self.balance[sym]
            tL[i][3] = '{:.3f}%'.format((self.tradingData[sym]['triggerRate']) * 100)
            tL[i][4] = '{:.3f}%'.format(self.tradingData[sym]['spreadRateFt'] * 100)
            tL[i][5] = '{:.3f}%'.format(self.tradingData[sym]['spreadRateSp'] * 100)
            tL[i][6] = '{:.3f}%'.format(self.tradingData[sym]['sfDiffRate'] * 100)
            # tL[i][6] = self.orderBookSp[sym]['bid'][1][0] #debug

        self.treeLists['sym'] = tL
        self.treeLists['common'] = [['{:.2f}%'.format(self.bnBalance.getLiqPercent())]]

    def _runGui(self):
        if self.flagGui:
            self._runSymTreeView()
            self.updateTreeView()
            self.root.update()

    async def run(self):
        while RUNNING_FLAG[0]:
            await asyncio.sleep(0.5)
            self._runGui()
        self.root.quit()
        self.root.destroy()

