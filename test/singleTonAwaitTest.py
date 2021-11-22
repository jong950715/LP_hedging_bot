import asyncio


class SingleToneAsyncInit:
    _ins = None

    @classmethod
    async def createIns(cls, *args, **kwargs):
        return await cls.getIns(*args, **kwargs)

    @classmethod
    async def getIns(cls, *args, **kwargs):
        if cls._ins:
            return cls._ins
        cls._ins = cls()
        await cls._ins.asyncInit(*args, **kwargs)
        return cls._ins

    def __new__(cls, *args, **kwargs):
        if cls._ins:
            raise Exception("반드시 getIns, createIns를 사용해주세요.")
        return super(SingleToneAsyncInit, cls).__new__(cls, *args, **kwargs)

    async def asyncInit(self, *args, **kwargs):
        # will be override
        await asyncio.sleep(0)
        print('asyncInit in AsyncInit')


class A(SingleToneAsyncInit):
    async def asyncInit(self, msg):
        self.msg = msg
        await asyncio.sleep(1)
        print('asyncInit in A')

    def printA(self):
        print(A, self.msg)


async def main():
    insA1 = await A.createIns('msg for arg')
    insA1.printA()
    insA2 = await A.getIns(msg='new message')
    insA2.printA()
    #insA3 = A()

    print(insA1)
    print(insA2)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
