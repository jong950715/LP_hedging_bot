import telegram

token = "여기에_토큰을_넣어주세요."
id = "여기에_id를_넣어주세요."

bot = telegram.Bot(token)
bot.sendMessage(chat_id=id, text="테스트 중입니다.")