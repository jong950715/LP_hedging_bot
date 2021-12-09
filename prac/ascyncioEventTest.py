import asyncio


async def sche(event):
    while True:
        await asyncio.sleep(1)
        event.set()


async def printer(event):
    while True:
        await event.wait()
        event.clear()
        print("ring")


async def main():
    ev = asyncio.Event()

    tasks = []
    tasks.append(asyncio.create_task(printer(ev)))
    tasks.append(asyncio.create_task(sche(ev)))

    await asyncio.wait(tasks)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())