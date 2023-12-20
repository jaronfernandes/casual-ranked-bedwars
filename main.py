"""
Written by: Jaron Fernandes   Last updated: 2023-12-9
Github: jaronfernandes
Repository: https://github.com/jaronfernandes/casual-ranked-bedwars

Copyright (c) 2023, jaronfernandes
See LICENSE for more details.
"""

from __future__ import annotations

import discord, os, json
import random
from datetime import date
from discord.ext import commands
from discord.ui import Button, button
from dotenv import load_dotenv
import matchmaking

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
# intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command("help")
bot.remove_command("stats")
bot.remove_command("rules")
bot.remove_command("season")


"""
        //ELO SYSTEM\\
    0 W: +35 L: -5 1ST: +15 2ND: +10 3RD: +5
    100 W: +35 L: -10 1ST: +15 2ND: +10 3RD: +5
    200 W: +30 L: -10 1ST: +15 2ND: +10 3RD: +5
    300 W: +25 L: -15 1ST: +10 2ND: +5
    400 W: +25 L: -20 1ST: +10 2ND: +5 
    500 W: +20 L: -20 1ST: +10 2ND: +5
    600 W: +15 L: -20 1ST: +10 2ND: +5
    700 W: +15 L: -25 1ST: +5 
    800 W: +10 L: -25 1ST: +5
    900 W: +10 L: -30 1ST: +5
    1000+ W: +10 L: -30
"""


## EVENTS


@bot.event
async def on_ready():
    await bot.tree.sync()

    for file in os.listdir("bot_commands"):
        if file.endswith(".py"):
            await bot.load_extension(f"bot_commands.{file[:-3]}")
            print(f"Loaded {file[:-3]}")

    print('Bot is ready.')
    

@bot.event
async def end():
    print("oof")
    await bot.close()


bot.run(BOT_TOKEN)