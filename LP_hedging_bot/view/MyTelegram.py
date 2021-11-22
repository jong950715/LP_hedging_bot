import asyncio

from common.SingleTonAsyncInit import SingleTonAsyncInit
from aiogram import Bot
from telegram import Bot as SyncBot
from collections import deque
from common.createTask import createTask


class MyTelegram(SingleTonAsyncInit):
    async def _asyncInit(self, apiToken, chatId: int):
        self.bot = Bot(apiToken)
        self.syncBot = SyncBot(apiToken)
        self.chatId = chatId
        self.sendQue = deque()
        self.latest = 0

    def sendMessageSync(self, msg: str):
        self.syncBot.sendMessage(chat_id=self.chatId, text=msg)

    def sendMessage(self, msg: str):
        self.sendQue.append(msg)

    async def flush(self):
        if self.sendQue:
            tasks = []
            for _ in range(len(self.sendQue)):
                msg = self.sendQue.popleft()
                tasks.append(createTask(self.bot.send_message(self.chatId, msg)))
            returns, pending = await asyncio.wait(tasks)

    async def recvRoutine(self):
        recvs = await self.bot.get_updates(self.latest+1)
        for r in recvs:
            if r.message:
                if r.message.chat.id == self.chatId:
                    self.consumer(r.message.text)
            elif r.edited_message:
                if r.edited_message.chat.id == self.chatId:
                    self.consumer(r.edited_message.text)
            else:
                pass
            self.latest = r.update_id

    async def checkLatest(self):
        recvs = await self.bot.get_updates(0)
        if recvs:
            self.latest = recvs[-1].update_id
        else:
            self.latest = 0

    def consumer(self, text):
        pass

    async def run(self):
        await self.checkLatest()
        while True:
            await self.flush()
            await self.recvRoutine()
            await asyncio.sleep(1)

