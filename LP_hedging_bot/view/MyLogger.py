import asyncio
import logging

from common.SingleTonAsyncInit import SingleTonAsyncInit
from definitions import getRootDir
from view.MyTelegram import MyTelegram
from collections import defaultdict

"""
콘솔로그
파일로그
텔레그램로그
"""
LOGGER_NAME = 'myLogger'
LOGGER_LEVEL = logging.DEBUG
LOG_FILE_NAME = '/view/AutoHedgeBot'
EAGER_THREASHOLD = 35


class MyFileHandler(logging.Handler):
    def __init__(self, filename, mode='a', encoding="UTF-8", errors=None):
        logging.Handler.__init__(self)
        self.file = open(filename, mode, encoding=encoding, errors=errors)

    def close(self):
        self.file.close()
        logging.Handler.close(self)

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.file.write(msg)
        if record.levelno > EAGER_THREASHOLD:
            self.myFlush()

    def myFlush(self) -> None:
        # Sync flush is fast enough
        self.file.flush()


class TeleGramHandler(logging.Handler):
    def __init__(self, myTelegram: MyTelegram):
        logging.Handler.__init__(self)
        self.telegram = myTelegram

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        if record.levelno > EAGER_THREASHOLD:
            self.telegram.sendMessageSync(msg)
        else:
            self.telegram.sendMessage(msg)

    async def myFlush(self) -> None:
        # MyTelegram is flushed by itself regularly
        await asyncio.sleep(0)


class MyLogger(SingleTonAsyncInit):
    async def _asyncInit(self, myTelegram: MyTelegram, configLogger):
        self.config = configLogger
        self.logger = logging.getLogger(LOGGER_NAME)
        self.logger.setLevel(LOGGER_LEVEL)
        formatter = logging.Formatter(
            '\n|%(asctime)s|'
            '\n##%(levelname)s##'
            '\n%(message)s'
            '\n\t >> File "%(filename)s", line %(lineno)s, in %(module)s\n\n')

        self.consoleHandler = logging.StreamHandler()
        self.fileHandler = MyFileHandler(filename = getRootDir() + LOG_FILE_NAME)
        self.teleHandler = TeleGramHandler(myTelegram)

        self.handlers = [self.consoleHandler, self.fileHandler, self.teleHandler]

        for h in self.handlers:
            h.setFormatter(formatter)
            self.logger.addHandler(h)

        # flags에 직접 접근 절대 금지
        self.flags = defaultdict(lambda: self.defaultNewFlag())  # flags['name'] = [flag, period]
        self.timer = defaultdict(lambda: [[0], set()])  # timer[period] = [[cnt], names]

    def getLogger(self):
        return self.logger

    def defaultNewFlag(self):
        newPeriod = self.config['config']['default_period'] / self.config['config']['base_period']
        if 'minValue' in self.newKey:
            newPeriod = self.config['config']['min_value_period']/self.config['config']['base_period']
        self.timer[newPeriod][1].add(self.newKey)
        return [False, newPeriod]

    def accessFlags(self, key):
        self.newKey = key
        return self.flags[key]

    def checkFlags(self, flagName):
        res = self.accessFlags(flagName)[0]
        self.accessFlags(flagName)[0] = True
        return res

    def warningWithFlag(self, msg, flagName):
        if self.checkFlags(flagName):
            return
        self.logger.warning(msg)

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

    async def run(self):
        # flush every 10seconds
        while True:
            await asyncio.sleep(self.config['config']['base_period'])
            self.fileHandler.myFlush()
            self.scheduler()


async def example():
    myTelegram = await MyTelegram.createIns('2126605846:AAErZbnd9wLBEIrzi-r47kjV1H83FlHaKas', 1915409831)
    myLogger = await MyLogger.getIns(myTelegram)

    MyLogger.getInsSync().setPeriodOfFlagName('flagB', 30)
    MyLogger.getInsSync().setPeriodOfFlagName('flagC', 10)

    tasks = []
    tasks.append(asyncio.create_task(myTelegram.run()))
    tasks.append(asyncio.create_task(myLogger.run()))
    tasks.append(asyncio.create_task(test1()))
    await asyncio.wait(tasks)


async def test1():
    if MyLogger.getInsSync().checkFlags('flagA') is False:
        MyLogger.getInsSync().getLogger().warning('flagA_60sec')

    if MyLogger.getInsSync().checkFlags('flagB') is False:
        MyLogger.getInsSync().getLogger().warning('flagB_30sec')

    if MyLogger.getInsSync().checkFlags('flagC') is False:
        MyLogger.getInsSync().getLogger().warning('flagC_10sec')

    await asyncio.sleep(0.01)


if __name__ == '__main__':
    loop_ = asyncio.get_event_loop()
    loop_.run_until_complete(example())
