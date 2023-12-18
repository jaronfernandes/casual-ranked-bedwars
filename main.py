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
    - max_players: The maximum number of players in the match.
    - players: A dictionaries of players in the match along with their ELO.
    - teams: A list of teams in the match.
    - map: A string representing the map the match was played on.
    - is_big_team_map: A boolean representing whether the map is a 3s/4s map.
    - is_ready: A boolean representing whether the match is ready to be played.
    - is_randomized_teams: A boolean representing whether the teams are randomized.
    - is_randomized_captains: A boolean representing whether the captains are randomized.
    """
    id: int
    date: str
    host: discord.User
    max_players: int = 2
    players: dict[str: int]
    teams: dict[str: list[str]]
    map: str
    is_big_team_map: bool
    is_ready: bool
    is_randomized_teams: bool
    is_randomized_captains: bool

    def __init__(self, id: int, date: str, max_players: int, players: dict[str: int], map: str, is_big_team_map: bool, host: discord.User) -> None:
        """Initialize a new match."""
        self.id = id
        self.host = host
        self.date = date
        self.max_players = max_players
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
    
    def get_max_players(self) -> int:
        """Return the maximum number of players in the match."""
        return self.max_players
    
    def get_randomized_teams(self) -> bool:
        """Return whether the match has randomized teams."""
        return self.is_randomized_teams
    
    def get_randomized_captains(self) -> bool:
        """Return whether the match has randomized captains."""
        return self.is_randomized_captains

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
    players: list[discord.User]
    img_file: discord.File
    embed: discord.Embed

    def __init__(self, match: Match, plr: discord.User):
        super().__init__()
        self.title = f"New Casual Ranked Bedwars Match {match.id}"
        self.match = match
        self.img_file = None
        self.players = [plr]
        self.embed = discord.Embed(
            title=self.title, 
            description=str(match),
            color=0x00ff00
        )

        self.embed.add_field(name="Players (" + str(len(self.players)) + "/" + str(self.match.get_max_players()) + ")", value=self._get_players_string(), inline=True)

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

        settings_str = \
            "Randomized Teams: " + ("Enabled" if self.match.get_randomized_teams() else "Disabled") + "\n" + \
            "Randomized Captains: " + ("Enabled" if self.match.get_randomized_captains() else "Disabled") + "\n" + \
            "Max Players: " + str(self.match.get_max_players()) + "\n" 

        self.embed.add_field(name="Settings", value=settings_str, inline=True)

    def get_embed(self) -> discord.Embed:
        """Return the embed."""
        return self.embed
    
    def get_file(self) -> discord.File:
        """Return the file."""
        return self.img_file
    
    def get_host(self) -> discord.User:
        """Return the host."""
        return self.match.get_host()
    
    def _get_players_string(self) -> str:
        """Return a string of players."""
        plrs_str = ""
        
        for player in self.players:
            plrs_str += "<@"+ str(player.id) + ">, "

        plrs_str = plrs_str.removesuffix(", ")

        return plrs_str
    
    def update_new_player(self, player: discord.User) -> None:
        """Update the embed to include a new player."""
        self.players.append(player)
        self.embed.set_field_at(name="Players", value=self._get_players_string(), inline=True)

    def remove_player(self, player: discord.User) -> None:
        """Remove a player from the embed."""
        self.players.remove(player)
        self.embed.set_field_at(name="Players", value=self._get_players_string(), inline=True)


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
                "current_season": {
                    "season": 1,
                    "total_games_played": 0,
                    "start_date": str(date.today()),
                    "end_date": "N/A",
                    "banned_items": ["Knockback Stick", "Pop-up Towers", "Obsidian", "Punch Bows"]
                },
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
                },
                "previous_season_statistics": {
                    # "1": {
                    #     "user_data": {},
                    #     "total_games_played": 0,
                    #     "start_date": "01/01/1970",
                    #     "end_date": "01/01/1970"
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


def create_match(player, playerscurrent_guild_id: int, is_big_team_map: bool = False, randomize_match: bool = False, max_players: int = 2) -> Match:
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
                data["SERVERS"][str(playerscurrent_guild_id)]["current_season"]["total_games_played"] += 1
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
                match_object = Match(match_id, todays_date, max_players, players, map, is_big_team_map, player)
                games_running[match_id] = match_object
                return match_object
    except:
        print("Error creating match.")
        return None
    

def get_season_embed(current_guild: discord.Guild) -> discord.Embed:
    """Return an embed for the current season.
    
    Preconditions:
    - current_guild_id is the ID of the current guild.
    """
    current_guild_id = current_guild.id

    with open("data", "r") as file:
        string = file.read()
        data = json.loads(string)

        if str(current_guild_id) not in data["SERVERS"]:
            setup_guild_in_json_file(current_guild_id)
            print(f"Created new server {current_guild_id} in data file.")

        current_season = data["SERVERS"][str(current_guild_id)]["current_season"]
        season = current_season["season"]
        start_date = current_season["start_date"]
        end_date = current_season["end_date"]
        banned_items = current_season["banned_items"]

        embed = discord.Embed(
            title= current_guild.name + " | Season " + str(season),
            description="Season " + str(season) + " started on " + start_date + (" and ended on " + end_date + "." if end_date != "N/A" else "."),
            # aqua colour
            color= 0x00ffff
        )

        plrs = []
        # get top players based on ELO below
        for player in data["SERVERS"][str(current_guild_id)]["user_data"]:
            plrs.append({
                "ID": player,
                "ELO": data["SERVERS"][str(current_guild_id)]["user_data"][player]["ELO"]
                })
        top_players = sorted(plrs, key=lambda k: k["ELO"], reverse=True)[:10]
        top_players_str = ""

        count = 1

        for player in top_players:
            top_players_str += f"{(str(count) + '. <@' + str(player['ID']) + '>') : <30}" + "\t ELO: " + str(player["ELO"]) + "\n"
            count += 1

        embed.add_field(name="Top Players", value=top_players_str, inline=False)

        embed.add_field(name="Banned Items", value=str(",\n".join(banned_items)), inline=True)

        season_stats_str = \
            "Total Matches: " + str(current_season["total_games_played"]) + "\n"

        embed.add_field(name="Season Statistics", value=season_stats_str)

        try:
            embed.set_thumbnail(url=current_guild.icon)
        except Exception as e:
            print(e)
            print("Error getting guild image embed.")

        return embed
    
    
def create_rules_embed(ctx):
    """Return an embed for the rules."""
    rules_embed = discord.Embed(
        title="Casual Ranked Bedwars Rules",
        description="Basic Rules for Casual Ranked Bedwars games.",
        # colour yellow
        color=0xffff00
    )
    
    # { name: "First Rusher:", value: "Gets 28-36 iron to buy blocks and bridges to mid and 2 stacks (sometimes a mix of 1, 2, and 3 stack in some cases", inline: true},
    # { name: "Second Rusher:", value: "Gets a base of 12 gold to buy iron armour, and a quantity of iron to get blocks/tools/swords", inline: true},
    # { name: "Third Rusher:", value: "Drops 15-25 iron to the defender. May also get iron armour, blocks/tools/swords, and other items (fireballs)", inline: true},
    # { name: "Fourth Rusher:", value: "Gets 64 + 8 iron (or 4 gold and 48 iron) to buy an endstone/wood butterfly defense, and places it down. They then follow the others to mid.", inline: true},
    
    rules_embed.add_field(name="First Rusher:", value="Gets 28-36 iron to buy blocks and bridges to mid and 2 stacks (sometimes a mix of 1, 2, and 3 stack in some cases", inline=False)
    rules_embed.add_field(name="Second Rusher:", value="Gets a base of 12 gold to buy iron armour, and a quantity of iron to get blocks/tools/swords", inline=False)
    rules_embed.add_field(name="Third Rusher:", value="Drops 15-25 iron to the defender. May also get iron armour, blocks/tools/swords, and other items (fireballs)", inline=False)
    rules_embed.add_field(name="Fourth Rusher:", value="Gets 64 + 8 iron (or 4 gold and 48 iron) to buy an endstone/wood butterfly defense, and places it down. They then follow the others to mid.", inline=False)

    try:
        rules_embed.set_thumbnail(url=ctx.guild.icon)
    except Exception as e:
        print(e)
        print("Error getting guild image embed.")
    return rules_embed


def create_help_embed(ctx):
    """Return an embed for the help menu."""
    help_embed = discord.Embed(
        title="Casual Ranked Bedwars Help Menu",
        description="Use Slash (/) Interactions or the prefix ! to execute commands.",
        # colour white
        color=0xffffff
    )

    help_embed.add_field(name="help", value="View the help menu.", inline=False)
    help_embed.add_field(name="play", value="Start a new game.", inline=False)
    help_embed.add_field(name="queue", value="View the queue for your current game.", inline=False)
    help_embed.add_field(name="stats", value="Get your current season statistics.", inline=False)
    help_embed.add_field(name="season", value="View the current season.", inline=False)
    help_embed.add_field(name="rules", value="View the rules and instructions for Casual Ranked Bedwars.", inline=False)
    help_embed.add_field(name="maps", value="View the maps currently in rotation.", inline=False)
    help_embed.add_field(name="lb", value="View the leaderboard.", inline=False)
    help_embed.add_field(name="winners", value="View the winners of the previous season.", inline=False)
    help_embed.add_field(name="score", value="Score a game [ADMINS ONLY]", inline=False)
    help_embed.add_field(name="reset-season", value="Reset the season to a new one [ADMINS ONLY]", inline=False)

    try:
        help_embed.set_thumbnail(url=ctx.guild.icon)
    except Exception as e:
        print(e)
        print("Error getting guild image embed.")
    return help_embed


## UI CLASSES
    
class RandomizeCaptains(discord.ui.View):
    match: Match
    has_interacted_with: bool

    def __init__ (self, match: Match) -> None:
        super().__init__()
        self.has_interacted_with = False
        self.match = match

    @button(label='Random', style=discord.ButtonStyle.primary, custom_id="randomize_button")
    async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True


        self.clear_items()

        self.match.set_randomized_captains()
        new_view = JoinGame(self.match, interaction.user)
        embedy = new_view.get_embed()
        filey = new_view.get_file()
        interaction.delete_original_response()

        await interaction.response.send_message(
            interaction.user.name+' is now hosting a match!', 
            ephemeral=False, 
            file=filey,
            embed=embedy,
            view=new_view)

    @button(label='Highest ELO', style=discord.ButtonStyle.primary, custom_id="non_randomize_button")
    async def non_randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True

        self.clear_items()

        self.match.set_randomized_captains(False)
        new_view = JoinGame(self.match, interaction.user)
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
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True

        self.clear_items()
        del players_in_game[interaction.user.name]
        await interaction.response.send_message(content='You canceled the match!', view=self)
    
class RandomizeTeams(discord.ui.View):
    match: Match
    has_interacted_with: bool

    def __init__ (self, match: Match) -> None:
        super().__init__()
        self.has_interacted_with = False
        self.match = match
    
    @button(label='Random', style=discord.ButtonStyle.primary, custom_id="randomize_button")
    async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True

        self.clear_items()

        self.match.set_randomized_teams()
        new_view = JoinGame(self.match, interaction.user)
        embedy = new_view.get_embed()
        filey = new_view.get_file()

        interaction.message.delete()

        await interaction.response.send_message(
            interaction.user.name+' is now hosting a match!', 
            ephemeral=False, 
            file=filey,
            embed=embedy,
            view=new_view)
                
    @button(label='Custom', style=discord.ButtonStyle.primary, custom_id="non_randomize_button")
    async def non_randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True

        self.clear_items()

        self.match.set_randomized_teams(False)
        new_view = RandomizeCaptains(self.match)
        await interaction.response.edit_message(content='Do you want to randomize team captains?', view=new_view)

    @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True

        self.clear_items()
        del players_in_game[interaction.user.name]
        await interaction.response.send_message(content='You canceled the match!', view=self)

class RandomizeMap(discord.ui.View):
    has_interacted_with: bool
    max_players: int

    def __init__(self, max_players: int) -> None:
        super().__init__()
        self.has_interacted_with = False
        self.max_players = max_players

    @button(label='Random', style=discord.ButtonStyle.primary, custom_id="randomize_button")
    async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True

        self.clear_items()
        match = create_match(interaction.user, interaction.guild.id, False, True, self.max_players)
        new_view = RandomizeTeams(match)
        await interaction.response.edit_message(content='Do you want to randomize teams?', view=new_view)

    @button(label='Custom', style=discord.ButtonStyle.primary, custom_id="non_randomize_button")
    async def non_randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True
        
        self.clear_items()
        match = create_match(interaction.user, interaction.guild.id, False, False, self.max_players)
        new_view = RandomizeTeams(match)
        await interaction.response.edit_message(content='Do you want to randomize teams?', view=new_view)

    @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True
        
        self.clear_items()
        del players_in_game[interaction.user.name]
        await interaction.response.send_message(content='You canceled the match!', view=self)


class UsingSmallerMaps(discord.ui.View):
    has_interacted_with: bool
    max_players: int

    def __init__(self, max_players: int) -> None:
        super().__init__()
        self.has_interacted_with = False
        self.max_players = max_players

    @button(label='Yes', style=discord.ButtonStyle.primary, custom_id="yes_button")
    async def yes_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True
        
        new_view = RandomizeMap(self.max_players)
        self.clear_items()
        await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)

    @button(label='No', style=discord.ButtonStyle.primary, custom_id="no_button")
    async def no_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True
        
        new_view = RandomizeMap(self.max_players)
        self.clear_items()
        await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)

    @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True
        
        self.clear_items()
        del players_in_game[interaction.user.name]
        await interaction.response.edit_message(content='You canceled the match!', view=self)


class CreateMatch(discord.ui.View):
    host: discord.User
    has_interacted_with: bool

    def __init__(self, host: discord.User) -> None:
        super().__init__()
        self.has_interacted_with = False
        self.host = host

    @button(label='2', style=discord.ButtonStyle.primary, custom_id="2_button")
    async def second_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)
        else:
            if self.has_interacted_with:
                await interaction.response.send_message('This message has expired!', ephemeral=True)
                return
            
            self.has_interacted_with = True
        
            new_view = UsingSmallerMaps(2)
            # self.clear_items()
            # await interaction.response.edit_message(content='Will you be using a 3s/4s map?', view=new_view)
            await interaction.response.send_message('Will you be using a 3s/4s map?', ephemeral=True, view=new_view)

        
    @button(label='4', style=discord.ButtonStyle.primary, custom_id="4_button")
    async def fourth_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)
        else:
            if self.has_interacted_with:
                await interaction.response.send_message('This message has expired!', ephemeral=True)
                return
        
            self.has_interacted_with = True
        
            new_view = UsingSmallerMaps(4)
            # self.clear_items()
            # await interaction.response.edit_message(content='Will you be using a 3s/4s map?', view=new_view)
            await interaction.response.send_message('Will you be using a 3s/4s map?', ephemeral=True, view=new_view)
    
    @button(label='6', style=discord.ButtonStyle.primary, custom_id="6_button")
    async def sixth_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)
        else:
            if self.has_interacted_with:
                await interaction.response.send_message('This message has expired!', ephemeral=True)
                return
        
            self.has_interacted_with = True
        
        
            new_view = RandomizeMap(6)
            # self.clear_items()
            # await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)
            await interaction.response.send_message('Do you want to randomize your map?', ephemeral=True, view=new_view)

    @button(label='8', style=discord.ButtonStyle.primary, custom_id="8_button")
    async def eighth_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)
        else:
            if self.has_interacted_with:
                await interaction.response.send_message('This message has expired!', ephemeral=True)
                return
        
            self.has_interacted_with = True
        

            new_view = RandomizeMap(8)
            # self.clear_items()
            # await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)
            await interaction.response.send_message('Do you want to randomize your map?', ephemeral=True, view=new_view)

    @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.host.id != interaction.user.id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)
        else:
            if self.has_interacted_with:
                await interaction.response.send_message('This message has expired!', ephemeral=True)
                return
        
            self.has_interacted_with = True
        

            del players_in_game[interaction.user.name]
            self.clear_items()
            await interaction.response.edit_message(content=interaction.user.name+' canceled the match!', view=self)
    
    
class JoinGame(discord.ui.View):
    """View for joining a game."""
    matching_embed: MatchMakeEmbed
    has_interacted_with: bool

    def __init__(self, match: Match, user: discord.User):
        super().__init__()
        self.has_interacted_with = False
        self.matching_embed = MatchMakeEmbed(match, user)

    def get_embed(self) -> discord.Embed:
        """Return the embed."""
        return self.matching_embed.get_embed()
    
    def get_file(self) -> discord.File:
        """Return the file."""
        return self.matching_embed.get_file()

    @button(label='Join', style=discord.ButtonStyle.primary, custom_id="join_button")
    async def join_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        if interaction.user.id == self.matching_embed.get_host().id:
            await interaction.response.send_message('You can\'t join your own match!', ephemeral=True)
        else:
            players_in_game[interaction.user.name] = True
            self.matching_embed.match.add_player(interaction.user.name, int(get_player_data_from_json_file(interaction.user, interaction.guild.id)["ELO"]))
            self.matching_embed.update_new_player(interaction.user)
            await interaction.response.send_message(interaction.user.name+' joined the match!', ephemeral=False)

    @button(label='Leave', style=discord.ButtonStyle.danger, custom_id="leave_button")
    async def leave_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        if interaction.user.id == self.matching_embed.get_host().id:
            await interaction.response.send_message('You can\'t leave your own match!', ephemeral=True)
        else:
            del players_in_game[interaction.user.name]
            games_running[self.matching_embed.match.id].remove_player(interaction.user.name)
            self.matching_embed.remove_player(interaction.user)
            await interaction.response.send_message(interaction.user.name+' left the match!', ephemeral=False)

    @button(label='Cancel', style=discord.ButtonStyle.danger, custom_id="cancel_match_button")
    async def cancel_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.matching_embed.get_host().id:
            await interaction.response.send_message('You are not the host!', ephemeral=True)
        else:
            if self.has_interacted_with:
                await interaction.response.send_message('This message has expired!', ephemeral=True)
                return
        
            self.has_interacted_with = True

            self.clear_items()
            for player in self.matching_embed.match.players:
                del players_in_game[player]
            del games_running[self.matching_embed.match.id]
            await interaction.response.send_message(content=interaction.user.name+' cancelled the match!', view=self)


## SLASH COMMANDS


@bot.tree.command(name = "commandname", description = "My first application Command")
async def first_command(interaction):
    await interaction.response.send_message("Hello!")


@bot.tree.command(name = "add", description = "Add (or retrieve) a user from data file.")
async def retrieve_data(interaction):
    data = get_player_data_from_json_file(interaction.user, interaction.guild.id)
    await interaction.response.send_message(data)


@bot.tree.command(name = "play", description = "Start a new game")
async def retrieve_data(interaction: discord.interactions.Interaction):
    # interaction.channel.send("Enter the amount of players you'd like to play with with (2,4,6,8).")

    if valid_for_matchmaking(interaction.user.name):
        players_in_game[interaction.user.name] = True
        viewe = CreateMatch(interaction.user)
        await interaction.response.send_message(content="Enter the amount of players you'd like to play with with (2,4,6,8).", view=viewe, ephemeral=True)
    else:
        await interaction.response.send_message(content='You\'re already in a game!', ephemeral=True)


@bot.tree.command(name = "queue", description = "View the queue for your current game")
async def queue(interaction: discord.interactions.Interaction):
    if not valid_for_matchmaking(interaction.user.name):
        match = games_running[interaction.user.name]
        await interaction.response.send_message(content=f"Match ID {match.id} on {match.date} hosted by <@{match.host.id}> on {match.map}.", ephemeral=True)


@bot.tree.command(name = "season", description = "View the current season")
async def season(interaction: discord.interactions.Interaction):
    await interaction.response.send_message(content="The current season is season 1.", embed=get_season_embed(interaction.guild.id), ephemeral=True)


@bot.tree.command(name = "help", description = "View the help menu")
async def help(interaction: discord.interactions.Interaction):
    help_embed = create_help_embed(interaction)

    await interaction.response.send_message(embed=help_embed, ephemeral=True)


@bot.tree.command(name = "rules", description = "View the rules for Casual Ranked Bedwars")
async def rules(interaction: discord.interactions.Interaction):
    rules_embed = create_rules_embed(interaction)

    await interaction.response.send_message(embed=rules_embed, ephemeral=True)


## EVENTS


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


@bot.command(name = "games", description = "View all the current games running")
async def games(ctx: commands.Context):
    pass


@bot.command(name = "queue", description = "View the queue for your current game.")
async def queue(ctx: commands.Context):
    pass


@bot.command(name = "stats", description = "Get your current season statistics")
async def stats(ctx: commands.Context):
    pass


@bot.command(name = "season", description = "View the current season")
async def season(ctx: commands.Context):
    await ctx.send(embed=get_season_embed(ctx.guild))


@bot.command(name = "help", description = "View the help menu")
async def help(ctx: commands.Context):
    help_embed = create_help_embed(ctx)

    await ctx.send(embed=help_embed)


@bot.command(name = "rules", description = "View the rules for Casual Ranked Bedwars")
async def rules(ctx: commands.Context):
    rules_embed = create_rules_embed(ctx)

    await ctx.send(embed=rules_embed)


@bot.event
async def end():
    await bot.close()


bot.run(BOT_TOKEN)