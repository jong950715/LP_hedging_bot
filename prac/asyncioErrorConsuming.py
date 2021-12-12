import asyncio
from common.createTask import *
import random
import time

NUM_OF_TEST = 100


async def mkError(t, e):
    await asyncio.sleep(t)
    if e:
        raise Exception('crashed')


async def test1(times, errors):
    tasks = [None] * NUM_OF_TEST
    for i in range(NUM_OF_TEST):
        tasks[i] = asyncio.create_task(mkError(times[i], errors[i]))
    done, pending = await asyncio.wait(tasks)
    for d in done:
        try:
            await d
        except Exception as e:
            pass
            # print("I caught:", repr(e))
            # print(traceback.format_exc())


async def testNoError(times, errors):
    tasks = [None] * NUM_OF_TEST
    for i in range(NUM_OF_TEST):
        tasks[i] = asyncio.create_task(noError(times[i], errors[i]))
    done, pending = await asyncio.wait(tasks)


async def noError(t, e):
    await asyncio.sleep(t)
    if e:
        pass


async def main():
    times = [random.uniform(1, 5) for _ in range(NUM_OF_TEST)]
    errors = [random.choice([True, False]) for _ in range(NUM_OF_TEST)]

    print('MaxTime : ', max(times))

    s = time.time()
    #await test1(times, errors)
    await testNoError(times, errors)
    end = time.time() - s

    print('time : ', end)
    print((end - max(times)) * 1000)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
