import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')
print(BOT_TOKEN)

intents = discord.Intents.all()
# intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Bot is ready.')

bot.login(BOT_TOKEN)
# bot.run(BOT_TOKEN)