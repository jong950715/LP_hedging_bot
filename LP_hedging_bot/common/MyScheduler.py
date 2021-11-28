from common.SingleTonAsyncInit import SingleTonAsyncInit
import asyncio
from collections import defaultdict
import schedule  # 기능은 파워풀하지만, 너무 무거움. 매 task 마다 시간 계속비교하고.. AWS free tier 를 위해 자작으로 최적화 ㄱㄱ


class MyScheduler(SingleTonAsyncInit):
    async def _asyncInit(self, configScheduler):
        self.config = configScheduler

        # flags에 직접 접근 절대 금지(read도 안됨). flags, timer는 연관된 자료임.
        # flags의 key는 name으로, timer에 담겨 있고,
        # timer의 key는 period로 flag에 담겨있다.
        # timer 대 flags는 1 : N의 관계!
        self.flags = defaultdict(lambda: self.defaultNewFlag())  # flags['name'] = [flag, period]
        self.timer = defaultdict(lambda: [[0], set()])  # timer[period] = [[cnt], names]

    def defaultNewFlag(self):
        # flags의 defaultdict의 생성자를 위한 함수
        newPeriod = self.config['config']['default_period'] / self.config['config']['base_period']

        if 'minValue' in self.newKey:
            newPeriod = self.config['config']['min_value_period'] / self.config['config']['base_period']
        if 'runningAlert' == self.newKey:
            newPeriod = self.config['config']['running_alert'] / self.config['config']['base_period']
        self.timer[newPeriod][1].add(self.newKey)
        return [False, newPeriod]

    def accessFlags(self, key):
        # defaultdict는 newKey에 대한 인자를 던져주지 않기 때문에 직접 구현
        self.newKey = key
        return self.flags[key]

    def checkFlags(self, flagName):
        res = self.accessFlags(flagName)[0]
        self.accessFlags(flagName)[0] = True
        return res

    def setFlagNameInPeriod(self, flagName, newPeriod):
        self.setPeriodOfFlagName(flagName, newPeriod)

    def setPeriodOfFlagName(self, flagName, newPeriod):
        newPeriod = newPeriod / self.config['config']['base_period']
        oldPeriod = self.accessFlags(flagName)[1]

        self.accessFlags(flagName)[1] = newPeriod

        names = self.timer[oldPeriod][1]
        names.remove(flagName)

        self.timer[newPeriod][1].add(flagName)

    def resetFlags(self, names):
        for name in names:
            self.flags[name][0] = False

    def scheduler(self):
        for period, (cnt, names) in self.timer.items():
            cnt[0] += 1
            if period <= cnt[0]:
                cnt[0] = 0
                self.resetFlags(names)

    def tuneOclock(self):
        pass

    def updatePeriod(self):
        pass

    async def run(self):
        while True:
            await asyncio.sleep(self.config['config']['base_period'])
            self.scheduler()
