"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging

from aiogram import Bot, Dispatcher, executor, types
import asyncio

API_TOKEN = '2126605846:AAErZbnd9wLBEIrzi-r47kjV1H83FlHaKas'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        '''
        # Old fashioned way:
        await bot.send_photo(
            message.chat.id,
            photo,
            caption='Cats are here 😺',
            reply_to_message_id=message.message_id,
        )
        '''

        await message.reply_photo(photo, caption='Cats are here 😺')


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)


async def myTest1():
    r = await bot.get_updates()
    if r:
        latest = r[-1].update_id
    else:
        latest = 0
    while True:
        #r = await bot.get_chat(1915409831)
        #s =await bot.send_message(1915409831,'hihihi')
        r = await bot.get_updates(offset=latest+1)
        for a in r:
            if a.message:
                print(a.message.text, a.update_id, a.message.chat.id)
            elif a.edited_message:
                print(a.edited_message.text, a.update_id, a.edited_message.chat.id)
            else:
                print('에러에러~', a)
            latest = a.update_id


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(myTest1())
