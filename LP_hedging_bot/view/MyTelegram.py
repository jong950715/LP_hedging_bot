import asyncio
import re
import json

from common.SingleTonAsyncInit import SingleTonAsyncInit
from aiogram import Bot
from telegram import Bot as SyncBot
from collections import deque
from common.createTask import createTask
from config.config import *


class MyTelegram(SingleTonAsyncInit):
    async def _asyncInit(self, apiToken, chatId: int, configs):
        self.bot = Bot(apiToken)
        self.syncBot = SyncBot(apiToken)
        self.chatId = chatId
        self.sendQue = deque()
        self.latest = 0
        self.configs = configs

        self.findFunction = re.compile('(^[\w]*)\(')
        self.findParens = re.compile('^[\w]*(\([^()]*\))')
        self.findParams = re.compile('[^\s(),]+')

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
        recvs = await self.bot.get_updates(self.latest + 1)
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
        try:
            self._consumer(text)
        except IndexError as e:
            self.sendMessage('잘못된 형식')
        except KeyError as e:
            self.sendMessage('잘못된 형식 또는 인자')
        except Exception as e:
            self.sendMessage(str(e))

    def _consumer(self, text):
        func = self.findFunction.findall(text)[0]
        paren = self.findParens.findall(text)[0]
        params = self.findParams.findall(paren)
        self.sendMessage('func : {0}'
                         '\nparens : {1}'
                         '\nparams : {2}'
                         .format(func, paren, params))
        if func and paren:
            self.processCommand(func, params)

    def processCommand(self, func, params):
        if (func.lower() == 'showConfigs'.lower()) or (func.lower() == 'showAllConfig'.lower()):
            self.sendMessage(json.dumps(self.configs, sort_keys=False, indent=4))

        if (func.lower() == 'showConfig'.lower()) or (func.lower() == 'getConfig'.lower()):
            con = self.configs
            for param in params:
                con = con[param]
            self.sendMessage(json.dumps(con, sort_keys=False, indent=4))

        if func.lower() == 'setConfig'.lower():
            if len(params) != 4:
                self.sendMessage('인자가 4개 이어야 합니다.')
                return
            self.configs[params[0]][params[1]][params[2]] = convertType(params[3])
            config = getConfigFromFile(CONFIG_FILE_NAME[params[0]])
            config.set(params[1], params[2], params[3])
            with open(CONFIG_FILE_NAME[params[0]], 'w') as configFile:
                config.write(configFile)
            msg = '[{0}][{1}][{2}]가 {3}로 변경되었습니다.'.format(params[0], params[1], params[2], params[3])
            self.sendMessage(msg)

    async def run(self):
        await self.checkLatest()
        while True:
            await self.flush()
            await self.recvRoutine()
            await asyncio.sleep(1)
