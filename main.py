"""
Written by: Jaron Fernandes   Last updated: 2023-12-9
Github: jaronfernandes
Repository: https://github.com/jaronfernandes/casual-ranked-bedwars

Copyright (c) 2023, jaronfernandes
See LICENSE for more details.
"""


import discord, os, json
from discord.ext import commands
from discord import ui   # For buttons
import interactions
from interactions import Button, ButtonStyle
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
# intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

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

## CLASSES

class Match:
    """Class for a ranked bedwars match.
    
    Instance Attributes:
    - id: A unique identifier for the match.
    - date: The date the match was played on.
    - players: A dictionaries of players in the match along with their ELO.
    - teams: A list of teams in the match.
    - map: A string representing the map the match was played on.    
    """
    id: int
    date: str
    players: dict[str: int]
    teams: list
    map: str

    def __init__(self, id: int, date: str, teams: list, map: str) -> None:
        """Initialize a new match."""
        self.id = id
        self.date = date
        self.players = {}
        self.teams = teams
        self.map = map

    def player_in_match(self, player: str) -> bool:
        """Return whether player is in the match."""
        return player in self.players

    def add_player(self, player: str, player_elo: str) -> None:
        """Add a player to the match.
        
        Preconditions: player not in self.players
        """
        self.players[player] = player_elo

    def remove_player(self, player: str) -> None:
        """Remove a player from the match.
        
        Preconditions: player in self.players
        """
        del self.players[player]
    
    def __str__(self) -> str:
        """Return a string representation of this match."""
        return f"Match {self.id} on {self.date} with {self.players} on {self.map}."

## GLOBAL VARIABLES

games_running = {}
players_in_game = {}

## FUNCTIONS

def setup_guild_in_json_file(guild_id: int) -> None:
    """Set up a guild in the data file.
    
    Preconditions:
    - guild_id is a valid Discord guild ID.
    """
    with open("data", "r") as file:
        string = file.read()
        data = json.loads(string)
        if str(guild_id) not in data["SERVERS"]:
            data["SERVERS"][str(guild_id)] = {
                "admin_roles_id": 123456789,
                "scorer_roles_ids": 123456789,
                "CONCURRENT_MATCH_LIMIT": 0,
                "COUNT_TOP_KILLS": True,
                "games_played": 0,
                "user_data": {},
                "server_channels": {
                    # "test_channel_ID": {
                    #     "Name": "",
                    #     "Colour": "000000"
                    # }
                },
                "server_roles": {
                    # "test_role_ID": {
                    #     "Name": "",
                    #     "Colour": "000000",
                    #     "Position": 0
                    # }
                }
            }
            with open("data", "w") as jsonFile:
                json.dump(data, jsonFile)

def get_player_data_from_json_file(player, current_guild_id: int) -> dict:
    """Return a dictionary of player data from a file.
    
    Preconditions:
    - player is a valid Discord user (the author of the message, preferably).
    """
    player_name = player.name
    player_id = str(player.id)

    with open(f"data", "r") as file:
        string = file.read()
        data = json.loads(string)

        if str(current_guild_id) not in data["SERVERS"]:
            setup_guild_in_json_file(current_guild_id)
            print(f"Created new server {current_guild_id} in data file.")
            with open(f"data", "r") as file:
                string = file.read()
                data = json.loads(string)

        if player_id in data["SERVERS"][str(current_guild_id)]["user_data"]:
            print(f"Returning data for player {player_name}")
            return data["SERVERS"][str(current_guild_id)]["user_data"][player_id]
        else:  # Add the player and new data to it.
            new_data = {
                "Name": player_name,
                "Wins": 0,
                "Losses": 0,
                "Winstreak": 0,
                "ELO": 0
            }
            
            data["SERVERS"][str(current_guild_id)]["user_data"][player_id] = new_data
            with open("data", "w") as jsonFile:
                json.dump(data, jsonFile)

            print(f"Created new data for player {player_name}")
            return data["SERVERS"][str(current_guild_id)]["user_data"][player_id]
        
## UI CLASSES

class CreateMatch(discord.ui.View):
    async def on_button_click(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('You pressed a button!', ephemeral=True)

## EVENTS

@bot.tree.command(name = "commandname", description = "My first application Command")
async def first_command(interaction):
    await interaction.response.send_message("Hello!")

@bot.tree.command(name = "add", description = "Add (or retrieve) a user from data file.")
async def retrieve_data(interaction):
    data = get_player_data_from_json_file(interaction.user, interaction.guild.id)
    await interaction.response.send_message(data)

@bot.tree.command(name = "play", description = "Start a new game")
async def retrieve_data(interaction):
    interaction.channel.send("Enter the amount of players you'd like to play with with (2,4,6,8).")

    viewe = CreateMatch()
    button2 = discord.ui.Button(label="2", style=discord.ButtonStyle.primary, custom_id="2_button")
    button4 = discord.ui.Button(label="4", style=discord.ButtonStyle.primary, custom_id="4_button")
    button6 = discord.ui.Button(label="6", style=discord.ButtonStyle.primary, custom_id="6_button")
    button8 = discord.ui.Button(label="8", style=discord.ButtonStyle.primary, custom_id="8_button")
    button_cancel = discord.ui.Button(label="Cancel Match", style=discord.ButtonStyle.danger, custom_id="cancel_button")
    viewe.add_item(button2)
    viewe.add_item(button4)
    viewe.add_item(button6)
    viewe.add_item(button8)
    viewe.add_item(button_cancel)
   
    await interaction.channel.send(view=viewe)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Bot is ready.')

    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not message.content.startswith('!'):
        return
    
    if message.content.startswith('!add'):
        get_player_data_from_json_file(message.author, message.guild.id)
        await message.channel.send('Added player '+message.author.name+" to the data file!")    
    if message.content.startswith('!play'):
        await message.channel.send("Enter the amount of players you'd like to play with with (2,4,6,8).");

        viewe = CreateMatch()
        button2 = discord.ui.Button(label="2", style=discord.ButtonStyle.primary, custom_id="2_button")
        button4 = discord.ui.Button(label="4", style=discord.ButtonStyle.primary, custom_id="4_button")
        button6 = discord.ui.Button(label="6", style=discord.ButtonStyle.primary, custom_id="6_button")
        button8 = discord.ui.Button(label="8", style=discord.ButtonStyle.primary, custom_id="8_button")
        button_cancel = discord.ui.Button(label="Cancel Match", style=discord.ButtonStyle.danger, custom_id="cancel_button")
        viewe.add_item(button2)
        viewe.add_item(button4)
        viewe.add_item(button6)
        viewe.add_item(button8)
        viewe.add_item(button_cancel)

        await message.channel.send(view=viewe)

    if message.content.startswith('oof'):
        await message.channel.send('Bye!')


@bot.event
async def end():
    await bot.close()

bot.run(BOT_TOKEN)