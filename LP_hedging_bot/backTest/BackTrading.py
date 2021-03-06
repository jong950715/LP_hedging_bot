import csv
import datetime
from collections import defaultdict
from decimal import Decimal

from backTest.testCommon import toDecimal
from trading.BnTrading import BnTrading


class BackTrading(BnTrading):
    def backInit(self, length, inPrice, slip):
        # debt 추가 필요해보임.

        # 값 주입
        self.orderInfo['USDT']['priceStep'] = Decimal('0.0001')

        # 입력받은거 저장
        self.length = length
        self.inPrice = inPrice  # [sym][i]
        self.slip = toDecimal(slip)

        # 파밍 포지션, 바낸 포지션, netWorth
        self.backRes = defaultdict(lambda: [[0, 0, 0] for _ in range(length)])  # [sym][i][farm, bn1, price]

        # 첫 줄 설정
        for sym in self.pSymbols[0]:
            self.setPriceBalance(i=0)

        # 초기값
        index = 0

        self.calcTargetBalance()
        for sym in self.pSymbols[0]:
            self.backRes[sym][index][0] = toDecimal(self.poolSize[sym])
            self.backRes[sym][index][1] = toDecimal(self.targetBalance[sym])
            self.backRes[sym][index][2] = toDecimal(self.inPrice[sym][index])

        sym = 'USDT'
        self.backRes[sym][index][0] = toDecimal(self.poolSize[sym])
        self.backRes[sym][index][1] = toDecimal(self.targetBalance[sym])
        self.backRes[sym][index][2] = toDecimal('1')

        net = 0
        hodl = 0
        for sym in self.pSymbols[0]:
            net += (self.backRes[sym][index][0] + self.backRes[sym][index][1]) * self.backRes[sym][index][2]
            hodl += (self.backRes[sym][0][0] + self.backRes[sym][0][1]) * self.backRes[sym][index][2]
        sym = 'USDT'
        net += (self.backRes[sym][index][0] + self.backRes[sym][index][1]) * self.backRes[sym][index][2]
        hodl += (self.backRes[sym][0][0] + self.backRes[sym][0][1]) * self.backRes[sym][index][2]

        self.backRes['RESULT'][index][0] = net
        self.backRes['RESULT'][index][1] = hodl

    def getFarmSize(self, i):
        for k, v in self.backRes.items():
            v[i][0] = Decimal('0')

        for key, configPool in self.configPools.items():
            sym1 = configPool['sym1']
            sym2 = configPool['sym2']
            k = configPool['k']
            p1 = (float(self.orderBookSp[sym1]['bid'][0][0]) + float(self.orderBookSp[sym1]['ask'][0][0])) / 2
            p2 = (float(self.orderBookSp[sym2]['bid'][0][0]) + float(self.orderBookSp[sym2]['ask'][0][0])) / 2
            # deprecated

    def testStepWithOrder(self, i, orders):
        # 정보 업뎃 [farm, bn1, price]
        for sym in self.pSymbols[0]:
            self.backRes[sym][i][0] = toDecimal(self.poolSize[sym])
            self.backRes[sym][i][1] = self.backRes[sym][i - 1][1]
            self.backRes[sym][i][2] = toDecimal(self.inPrice[sym][i])

        sym = 'USDT'
        self.backRes[sym][i][0] = toDecimal(self.poolSize[sym])
        self.backRes[sym][i][1] = self.backRes[sym][i - 1][1]
        self.backRes[sym][i][2] = toDecimal('1')

        # order 처리
        for (sym, price, qty) in orders:  # (sym, price, qty)
            if sym == 'USDT':
                continue
            qty = toDecimal(qty)
            self.backRes[sym][i][1] += qty
            self.backRes['USDT'][i][1] -= qty * price
            self.backRes['USDT'][i][1] -= abs(qty * price) * self.slip

        net = 0
        hodl = 0
        for sym in self.pSymbols[0]:
            net += (self.backRes[sym][i][0] + self.backRes[sym][i][1]) * self.backRes[sym][i][2]
            hodl += (self.backRes[sym][0][0] + self.backRes[sym][0][1]) * self.backRes[sym][i][2]
        sym = 'USDT'
        net += (self.backRes[sym][i][0] + self.backRes[sym][i][1]) * self.backRes[sym][i][2]
        hodl += (self.backRes[sym][0][0] + self.backRes[sym][0][1]) * self.backRes[sym][i][2]

        self.backRes['RESULT'][i][0] = net
        self.backRes['RESULT'][i][1] = hodl

    def setPriceBalance(self, i):
        for sym in self.pSymbols[0]:
            self.orderBookFt[sym]['bid'][0][0] = self.inPrice[sym][i]
            self.orderBookFt[sym]['ask'][0][0] = self.inPrice[sym][i]
            self.orderBookSp[sym]['bid'][0][0] = self.inPrice[sym][i]
            self.orderBookSp[sym]['ask'][0][0] = self.inPrice[sym][i]

            if i:
                self.balance[sym] = self.backRes[sym][i - 1][1]

    def backRun(self):
        for i in range(1, self.length):
            self.setPriceBalance(i)  # 가격, 잔고 주입

            # 실제 함수
            self.calcTargetBalance()
            orders = self.generateOrderList()  # (sym, price, qty)

            # 백테스팅
            self.testStepWithOrder(i, orders)

        return (self.backRes['RESULT'][-1][0] - self.backRes['RESULT'][-1][1])

    def exportCsv(self, maxL=0):
        keys = list(self.backRes.keys())

        keys.remove('RESULT')
        keys.remove('USDT')

        cols = len(keys) * 4 + 6

        if maxL and maxL < self.length:
            n = self.length // maxL
        else:
            maxL = self.length
            n = 1

        current_time = datetime.datetime.now().__str__().replace(':', ';')
        with open('{}.csv'.format(current_time), 'w', encoding='utf-8', newline='') as csvfile:
            csvWriter = csv.writer(csvfile)

            row = ['' for _ in range(cols)]
            for j, k in enumerate(keys):
                row[j * 4] = '{} farm'.format(k)
                row[j * 4 + 1] = '{} hedged'.format(k)
                row[j * 4 + 2] = '{} price'.format(k)

            row[-6] = 'USDT farm'
            row[-5] = 'USDT hedged'
            row[-4] = 'USDT price'
            row[-2] = 'NET'
            row[-1] = 'HODL'
            csvWriter.writerow(row)

            for i in range(maxL):
                idx = int(n * i)
                row = ['' for _ in range(cols)]

                # 일반 코인
                for j, k in enumerate(keys):
                    for ii in range(3):
                        row[j * 4 + ii] = self.backRes[k][idx][ii]

                # 테더
                for ii in range(3):
                    row[-6 + ii] = self.backRes['USDT'][idx][ii]

                # NET
                row[-2] = self.backRes['RESULT'][idx][0]
                row[-1] = self.backRes['RESULT'][idx][1]

                csvWriter.writerow(row)

    async def sweepTest(self, trigL, trigH, tSamp, slipL, slipH, sSamp):
        trigItv = (trigH - trigL) / (tSamp - 1)
        slipItv = (slipH - slipL) / (sSamp - 1)

        trigs = [(trigL + trigItv * i) for i in range(tSamp)]
        slips = [(slipL + slipItv * i) for i in range(sSamp)]

        print('trigs : ', trigs)
        print('slips : ', slips)

        # trigger - x slip - y
        table = [[str(sl) for sl in slips]]
        for tr in trigs:
            print(await self.myConfig.setConfig(('configCommon', 'trading', 'diff_trigger_rate', str(tr))))
            row = [str(tr)]
            for sl in slips:
                self.backInit(length=self.length, inPrice=self.inPrice, slip=sl)
                row.append(self.backRun())
            table.append(row)

        self.table = table
        return table

    def exportSweepTest(self):
        current_time = datetime.datetime.now().__str__().replace(':', ';')
        with open('sweep_{}.csv'.format(current_time), 'w', encoding='utf-8', newline='') as csvfile:
            csvWriter = csv.writer(csvfile)
            for row in self.table:
                csvWriter.writerow(row)
