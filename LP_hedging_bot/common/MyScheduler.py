from common.SingleTonAsyncInit import SingleTonAsyncInit
import asyncio
from collections import defaultdict
from common.createTask import RUNNING_FLAG
# from common.createTask import createTask
# import schedule  # 기능은 파워풀하지만, 너무 무거움. 매 task 마다 시간 계속비교하고.. AWS free tier 를 위해 자작으로 최적화 ㄱㄱ


class MyScheduler(SingleTonAsyncInit):
    async def _asyncInit(self, myConfig):
        self.config = myConfig.getConfig('configCommon')['scheduler']

        # flags에 직접 접근 절대 금지(read도 안됨). flags, timer는 연관된 자료임.
        # flags의 key는 name으로, timer에 담겨 있고,
        # timer의 key는 period로 flag에 담겨있다.
        # timer 대 flags는 1 : N의 관계!
        self.flags = defaultdict(lambda: self.defaultNewFlag())  # flags['name'] = [flag, period]
        self.timer = defaultdict(lambda: [[0], set()])  # timer[period] = [[cnt], names]

    def defaultNewFlag(self):
        # flags의 defaultdict의 생성자를 위한 함수
        newPeriod = self.config['default_period'] / self.config['base_period']

        if 'minValue' in self.newKey:
            newPeriod = self.config['min_value_period'] / self.config['base_period']
        if 'runningAlert' == self.newKey:
            newPeriod = self.config['running_alert_period'] / self.config['base_period']
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
        newPeriod = newPeriod / self.config['base_period']
        oldPeriod = self.accessFlags(flagName)[1]

        self.accessFlags(flagName)[1] = newPeriod

        names = self.timer[oldPeriod][1]
        if flagName in names:
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
        while RUNNING_FLAG[0]:
            await asyncio.sleep(self.config['base_period'])
            self.scheduler()


async def myScheduleExample1():
    configScheduler = getConfigScheduler()
    myScheduler = await MyScheduler.createIns(configScheduler)  # 직접 주입하지는 않고 알아서 가져다 쓰는걸로

    tasks = []
    tasks.append(asyncio.create_task(myScheduler.run()))
    tasks.append(asyncio.create_task(_myScheduleExample1()))
    await asyncio.wait(tasks)


async def _myScheduleExample1():
    while True:
        if MyScheduler.getInsSync().checkFlags('flagType{0}'.format('flagParam')) is False:
            print('do something')

        await asyncio.sleep(0.1)


async def myScheduleExample2():
    configScheduler = getConfigScheduler()
    myScheduler = await MyScheduler.createIns(configScheduler)  # 직접 주입하지는 않고 알아서 가져다 쓰는걸로
    customPeriod = 10
    MyScheduler.getInsSync().setPeriodOfFlagName('customFlagName', customPeriod)

    tasks = []
    tasks.append(asyncio.create_task(myScheduler.run()))
    tasks.append(asyncio.create_task(_myScheduleExample2()))
    await asyncio.wait(tasks)


async def _myScheduleExample2():
    while True:
        if MyScheduler.getInsSync().checkFlags('customFlagName') is False:
            print('do something')

        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(myScheduleExample2())
