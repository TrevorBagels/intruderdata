


from .bot import AssistantBot
from dotenv import dotenv_values
token = dotenv_values(".env")['token']

bot = AssistantBot()
try:
	bot.run(token)
except:
	print("token not valid.")