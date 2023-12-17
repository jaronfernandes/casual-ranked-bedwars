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
    - host: The host User of the match.
    - players: A dictionaries of players in the match along with their ELO.
    - teams: A list of teams in the match.
    - map: A string representing the map the match was played on.    
    """
    id: int
    date: str
    host: discord.User
    players: dict[str: int]
    teams: dict[str: list[str]]
    map: str
    is_big_team_map: bool
    is_ready: bool
    is_randomized_teams: bool
    is_randomized_captains: bool

    def __init__(self, id: int, date: str, players: dict[str: int], map: str, is_big_team_map: bool, host: discord.User) -> None:
        """Initialize a new match."""
        self.id = id
        self.host = host
        self.date = date
        self.players = players
        self.map = map
        self.is_big_team_map = is_big_team_map
        self.is_randomized_teams = False
        self.is_randomized_captains = False
        self.is_ready = False

    def get_id(self) -> int:
        """Return the ID of the match."""
        return self.id
    
    def get_host(self) -> discord.User:
        """Return the host of the match."""
        return self.host

    def player_in_match(self, player: str) -> bool:
        """Return whether player is in the match."""
        return player in self.players

    def add_player(self, player: str, player_elo: int) -> None:
        """Add a player to the match.
        
        Preconditions: player not in self.players
        """
        players_in_game[player] = True
        self.players[player] = player_elo

    def remove_player(self, player: str) -> None:
        """Remove a player from the match.
        
        Preconditions: player in self.players
        """
        del players_in_game[player]
        del self.players[player]

    def set_teams(self, teams: dict[str, list[str]]) -> None:
        """Set the teams of the match."""
        self.teams = teams

    def set_ready(self) -> None:
        """Set the match to ready."""
        self.is_ready = True

    def set_randomized_teams(self, randomized_teams: bool = True) -> None:
        """Set the match to have randomized teams."""
        self.is_randomized_teams = randomized_teams
        self.is_randomized_captains = randomized_teams

    def set_randomized_captains(self, randomized_captains: bool = True) -> None:
        """Set the match to have randomized captains."""
        self.is_randomized_captains = randomized_captains
    
    def __str__(self) -> str:
        """Return a string representation of this match."""
        return f"Match ID {self.id} on {self.date} hosted by <@{self.host.id}> on {self.map}."
    

class MatchMakeEmbed():
    match: Match
    title: str
    players: list[str]
    img_file: discord.File
    embed: discord.Embed

    def __init__(self, match: Match, plr: discord.User):
        super().__init__()
        self.title = f"New Casual Ranked Bedwars Match {match.id}"
        self.match = match
        self.img_file = None
        self.players = [plr.name]
        self.embed = discord.Embed(
            title=self.title, 
            description=str(match),
            color=0x00ff00
        )

        self.embed.add_field(name="Players", value=", ".join(self.players), inline=True)

        try:
            file = discord.File("map_images/"+match.map+".png", filename=match.map+".png")
            self.embed.set_image(url="attachment://" + file.filename)
            self.img_file = file
            print('embed set')
        except:
            print("No image found for map "+match.map+", using default instead.")
            file = discord.File("map_images/hypixel.png", filename="hypixel.png")
            self.embed.set_image(url="attachment://" + file.filename)
            self.img_file = file

    def get_embed(self) -> discord.Embed:
        """Return the embed."""
        return self.embed
    
    def get_file(self) -> discord.File:
        """Return the file."""
        return self.img_file
    
    def get_host(self) -> discord.User:
        """Return the host."""
        return self.match.get_host()
    
    def update_new_player(self, player: str) -> None:
        """Update the embed to include a new player."""
        self.players.append(player)
        self.embed.set_field_at(name="Players", value=", ".join(self.players), inline=True)

    def remove_player(self, player: str) -> None:
        """Remove a player from the embed."""
        self.players.remove(player)
        self.embed.set_field_at(name="Players", value=", ".join(self.players), inline=True)


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
        
def valid_for_matchmaking(player: str) -> bool:
    """Return whether a player is valid for matchmaking.
    
    Preconditions:
    - player is a valid Discord user (the author of the message, preferably).
    """
    return player not in players_in_game


def create_match(player, playerscurrent_guild_id: int, is_big_team_map: bool = False, randomize_match: bool = False) -> Match:
    """Return a new match.
    
    Preconditions:
    - player is the player who is hosting the match (their user)
    - len(players) == 2 or len(players) == 4 or len(players) == 6 or len(players) == 8
    - playerscurrent_guild_id is the ID of the current guild.
    """
    host_data = get_player_data_from_json_file(player, playerscurrent_guild_id)

    try:
        with open("data", "r") as file:
            string1 = file.read()
            data = json.loads(string1)
            games_played = data["SERVERS"][str(playerscurrent_guild_id)]["games_played"]

            match_id = games_played

            with open("data", "w") as jsonfile:
                data["SERVERS"][str(playerscurrent_guild_id)]["games_played"] += 1
                json.dump(data, jsonfile)

            todays_date = date.today()
            players = {player.name: host_data["ELO"]}
            # teams = matchmaking.matchmake(players, playerscurrent_guild_id)

            with open("maps", "r") as file:
                # csv file
                string2 = file.read()
                maps = string2.split("\n")

                if randomize_match:
                    map = random.choice(maps)
                else:
                    map = "Any"
                    print("The user may manually select their desired map.")

                print(match_id, todays_date, players, map, is_big_team_map)
                match_object = Match(match_id, todays_date, players, map, is_big_team_map, player)
                games_running[match_id] = match_object
                return match_object
    except:
        print("Error creating match.")
        return None


## UI CLASSES
    
class RandomizeCaptains(discord.ui.View):
    @button(label='Random Captains', style=discord.ButtonStyle.primary, custom_id="randomize_button")
    async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        match = create_match(interaction.user, interaction.guild.id, False, True)
        new_view = JoinGame(match, interaction.user)
        embedy = new_view.get_embed()
        filey = new_view.get_file()
        await interaction.response.send_message(
            interaction.user.name+' is now hosting a match!', 
            ephemeral=False, 
            file=filey,
            embed=embedy,
            view=new_view)

    @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        del players_in_game[interaction.user.name]
        await interaction.response.send_message(content='You canceled the match!', view=self)
    
class RandomizeTeams(discord.ui.View):
    @button(label='Random Teams', style=discord.ButtonStyle.primary, custom_id="randomize_button")
    async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        match = create_match(interaction.user, interaction.guild.id, True, True)
        new_view = JoinGame(match, interaction.user)
        embedy = new_view.get_embed()
        filey = new_view.get_file()
        await interaction.response.send_message(
            interaction.user.name+' is now hosting a match!', 
            ephemeral=False, 
            file=filey,
            embed=embedy,
            view=new_view)

    @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        del players_in_game[interaction.user.name]
        await interaction.response.send_message(content='You canceled the match!', view=self)

class RandomizeMap(discord.ui.View):
    @button(label='Random', style=discord.ButtonStyle.primary, custom_id="randomize_button")
    async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        match = create_match(interaction.user, interaction.guild.id, False, True)
        new_view = JoinGame(match, interaction.user)
        embedy = new_view.get_embed()
        filey = new_view.get_file()
        await interaction.response.send_message(
            interaction.user.name+' is now hosting a match!', 
            ephemeral=False, 
            file=filey,
            embed=embedy,
            view=new_view)

    @button(label='Not Random', style=discord.ButtonStyle.primary, custom_id="non_randomize_button")
    async def non_randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        match = create_match(interaction.user, interaction.guild.id, False, False)
        new_view = JoinGame(match, interaction.user)
        embedy = new_view.get_embed()
        filey = new_view.get_file()
        await interaction.response.send_message(
            interaction.user.name+' is now hosting a match!', 
            ephemeral=False, 
            file=filey,
            embed=embedy,
            view=new_view)

    @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        del players_in_game[interaction.user.name]
        await interaction.response.send_message(content='You canceled the match!', view=self)


class UsingSmallerMaps(discord.ui.View):
    @button(label='Yes', style=discord.ButtonStyle.primary, custom_id="yes_button")
    async def yes_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_view = RandomizeMap()
        self.clear_items()
        await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)

    @button(label='No', style=discord.ButtonStyle.primary, custom_id="no_button")
    async def no_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_view = RandomizeMap()
        self.clear_items()
        await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)

    @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        del players_in_game[interaction.user.name]
        await interaction.response.edit_message(content='You canceled the match!', view=self)


class CreateMatch(discord.ui.View):
    host: discord.User

    def __init__(self, host: discord.User) -> None:
        super().__init__()
        self.host = host

    @button(label='2', style=discord.ButtonStyle.primary, custom_id="2_button")
    async def second_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)

        new_view = UsingSmallerMaps()
        # self.clear_items()
        # await interaction.response.edit_message(content='Will you be using a 3s/4s map?', view=new_view)
        await interaction.response.send_message('Will you be using a 3s/4s map?', ephemeral=True, view=new_view)

        
    @button(label='4', style=discord.ButtonStyle.primary, custom_id="4_button")
    async def fourth_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)

        new_view = UsingSmallerMaps()
        # self.clear_items()
        # await interaction.response.edit_message(content='Will you be using a 3s/4s map?', view=new_view)
        await interaction.response.send_message('Will you be using a 3s/4s map?', ephemeral=True, view=new_view)
    
    @button(label='6', style=discord.ButtonStyle.primary, custom_id="6_button")
    async def sixth_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)
        
        new_view = RandomizeMap()
        # self.clear_items()
        # await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)
        await interaction.response.send_message('Do you want to randomize your map?', ephemeral=True, view=new_view)

    @button(label='8', style=discord.ButtonStyle.primary, custom_id="8_button")
    async def eighth_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)

        new_view = RandomizeMap()
        # self.clear_items()
        # await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)
        await interaction.response.send_message('Do you want to randomize your map?', ephemeral=True, view=new_view)

    @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)

        del players_in_game[interaction.user.name]
        self.clear_items()
        await interaction.response.edit_message(content=interaction.user.name+' canceled the match!', view=self)
    
    
class JoinGame(discord.ui.View):
    """View for joining a game."""
    matching_embed: MatchMakeEmbed

    def __init__(self, match: Match, user: discord.User):
        super().__init__()
        self.matching_embed = MatchMakeEmbed(match, user)

    def get_embed(self) -> discord.Embed:
        """Return the embed."""
        return self.matching_embed.get_embed()
    
    def get_file(self) -> discord.File:
        """Return the file."""
        return self.matching_embed.get_file()

    @button(label='Join', style=discord.ButtonStyle.primary, custom_id="join_button")
    async def join_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.matching_embed.get_host().id:
            await interaction.response.send_message('You can\'t join your own match!', ephemeral=True)
        else:
            players_in_game[interaction.user.name] = True
            self.matching_embed.match.add_player(interaction.user.name, int(get_player_data_from_json_file(interaction.user, interaction.guild.id)["ELO"]))
            self.matching_embed.update_new_player(interaction.user.name)
            await interaction.response.send_message(interaction.user.name+' joined the match!', ephemeral=False)

    @button(label='Leave', style=discord.ButtonStyle.danger, custom_id="leave_button")
    async def leave_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.matching_embed.get_host().id:
            await interaction.response.send_message('You can\'t leave your own match!', ephemeral=True)
        else:
            del players_in_game[interaction.user.name]
            games_running[self.matching_embed.match.id].remove_player(interaction.user.name)
            self.matching_embed.remove_player(interaction.user.name)
            await interaction.response.send_message(interaction.user.name+' left the match!', ephemeral=False)

    @button(label='Cancel', style=discord.ButtonStyle.danger, custom_id="cancel_match_button")
    async def cancel_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.matching_embed.get_host().id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)
        else:
            self.clear_items()
            for player in self.matching_embed.match.players:
                del players_in_game[player]
            del games_running[self.matching_embed.match.id]
            await interaction.response.send_message(content=interaction.user.name+' cancelled the match!', view=self)


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
    await interaction.channel.send_message("Enter the amount of players you'd like to play with with (2,4,6,8).", view=viewe)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Bot is ready.')
    
@bot.command(name = "add", description = "Add (or retrieve) a user from data file.")
async def add(ctx: commands.Context):
    get_player_data_from_json_file(ctx.author, ctx.guild.id)
    await ctx.send('Added player '+ctx.author.name+" to the data file!")    

@bot.command(name = "play", description = "Start a new game")
async def play(ctx: commands.Context):
    if valid_for_matchmaking(ctx.author.name):
        players_in_game[ctx.author.name] = True
        viewe = CreateMatch(ctx.author)
        await ctx.send(content="Enter the amount of players you'd like to play with with (2,4,6,8).", view=viewe)
    else:
        await ctx.send('You\'re already in a game!')

@bot.event
async def end():
    await bot.close()

bot.run(BOT_TOKEN)