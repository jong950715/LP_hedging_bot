import asyncio
import traceback
import sys


def createTask(coro):
    task = asyncio.create_task(coro)
    task.add_done_callback(_handle_task_result)
    return task


def _handle_task_result(task: asyncio.Task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # Task cancellation should not be logged as an error.
    except Exception as e:  # pylint: disable=broad-except
        fo = traceback.format_exc()
        # msg = 'Exception raised by task = %r \n' + str(task)
        # raise Exception(msg)
        #raise Exception(fo)
        print(fo)
        exit()


async def task1():
    while True:
        await asyncio.sleep(1)
        print('task1')


async def task2():
    while True:
        await asyncio.sleep(1)
        print('task2')
        await asyncio.sleep(1)
        print('task2 die')
        1/0
        # exit()
        # sys.exit()


async def main():
    tasks = []
    tasks.append(createTask(task1()))
    tasks.append(createTask(task2()))
    await asyncio.wait(tasks)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
