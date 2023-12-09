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

## FUNCTIONS


## EVENTS

@bot.tree.command(name = "commandname", description = "My first application Command")
async def first_command(interaction):
    await interaction.response.send_message("Hello!")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Bot is ready.')

    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('play'):
        await message.channel.send('Hello!')

    if message.content.startswith('oof'):
        await message.channel.send('Bye!')

@bot.event
async def end():
    await bot.close()

bot.run(BOT_TOKEN)