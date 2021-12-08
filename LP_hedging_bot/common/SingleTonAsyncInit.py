import asyncio

'''
메소드 이름좀 바꾸자
'''


class SingleTonAsyncInit:
    _ins = None
    chkGetIns = False

    @classmethod
    async def createIns(cls, *args, **kwargs):
        # same to getIns
        return await cls.getIns(*args, **kwargs)

    @classmethod
    async def getIns(cls, *args, **kwargs):
        # This method ensures ins of cls is made
        if cls._ins:
            return cls._ins
        cls.chkGetIns = True
        try:
            cls._ins = cls()
        except TypeError:
            raise NotImplementedError('_asyncInit must be implemented. Do not use __init__') #
        await cls._ins._asyncInit(*args, **kwargs)
        return cls._ins

    @classmethod
    def getInsSync(cls):
        # This method doesn't ensure ins of cls is made
        if cls._ins:
            return cls._ins
        raise Exception("instance never created") #

    def __new__(cls, *args, **kwargs):
        if cls._ins:
            raise Exception("싱글턴 입니다. 반드시 getIns, createIns를 사용해주세요.")
        if cls.chkGetIns:
            return super(SingleTonAsyncInit, cls).__new__(cls, *args, **kwargs)
        raise Exception("Use createIns or getIns") #

    async def _asyncInit(self, *args, **kwargs):
        # will be override
        await asyncio.sleep(0)
        raise NotImplementedError('_asyncInit must be implemented. Do not use __init__') #

    @classmethod
    def selfDestruct(cls):
        cls._ins = None
        cls.chkGetIns = False


class MyClass(SingleTonAsyncInit):
    def __init__(self):
        self.msg = None  # 필요없는 함수지만 자동완성이 안되어서ㅠㅠ

    async def _asyncInit(self, msg):
        self.msg = msg
        await asyncio.sleep(1)
        print('asyncInit in Myclass')

    def myPrint(self):
        print(self.msg)


async def example():
    myIns = await MyClass.createIns("myIns Init Msg")
    myIns2 = await MyClass.createIns()

    print(myIns)
    print(myIns2)

    example2()


def example2():
    myIns = MyClass.getInsSync()
    print(myIns)
    myIns.myPrint()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(example())
