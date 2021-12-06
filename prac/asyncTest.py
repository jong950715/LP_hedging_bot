import asyncio

# Ref: https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.get_event_loop
# > If there is no current event loop set in the current OS thread,
# > the OS thread is main, and set_event_loop() has not yet been called,
# > asyncio will create a new event loop and set it as the current one
loop = asyncio.get_event_loop()

# So, loop2 is loop
loop2 = asyncio.get_event_loop()

print('loop is loop2: ', loop is loop2)


async def main(
        _loop,
        desc: str
):
    if asyncio.get_running_loop() is _loop:
        print(desc, ': match')
    else:
        print(desc, ': not match')


# Ref: https://docs.python.org/3/library/asyncio-task.html#asyncio.run
# > This function always creates a new event loop and closes it at the end.
# > It should be used as a main entry point for asyncio programs,
# > and should ideally only be called once.
asyncio.run(main(loop, 'asyncio.run'))

# The output is:
# $ asyncio.run : not match

# Because `asyncio.run()` does following things:
# - create a new event loop
# - set the newly-created event loop as the current event loop
# - run the coroutine util completed
# - set the current event loop as None
#
# ```python
# new_loop = asyncio.new_event_loop()
# asyncio.set_event_loop(new_loop)
# new_loop.run_until_complete(coro)
# asyncio.set_event_loop(None)
# loop.close()
# ```

loop.run_until_complete(main(loop, 'loop.run_until_complete'))

try:
    loop3 = asyncio.get_event_loop()
except Exception as e:
    print('asyncio.get_event_loop() exception after asyncio:', e)

    # Why?

loop.run_until_complete(main(loop, 'loop.run_until_complete'))

# The output is
# $ loop.run_until_complete : match

# As explained above, we need to set the current event loop explicitly.
asyncio.set_event_loop(loop)

asyncio.get_event_loop().run_until_complete(
    main(loop, 'asyncio.get_event_loop().run_until_complete')
)

# The output is
# $ asyncio.get_event_loop().run_until_complete : match

# Conclusion
# - never use `asyncio.run()` in frameworks, or you might break the code of others
# - be careful by using `asyncio.run()`, or it is recommended that you manage the event loop your own
