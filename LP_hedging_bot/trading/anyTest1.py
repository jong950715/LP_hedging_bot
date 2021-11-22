import asyncio


async def func1(i):
    print("start : ", i)
    await asyncio.sleep(5)
    print("finish : ", i)


async def main():
    tasks = []
    for i in range(10):
        tasks.append(asyncio.create_task(func1(i)))
        print('for : ', i)

    returns, pending = await asyncio.wait(tasks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
