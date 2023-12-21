import discord, os, json, random
from datetime import date
from entities import Match, MatchMakeEmbed
from discord.ui import button


## TEMPORARY DATA


_games_running = {}
_players_in_game = {}


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

        await interaction.response.send_message(
            '<@' + str(interaction.user.id) +'> is now hosting a match!', 
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
            '<@' + str(interaction.user.id) +'> is now hosting a match!', 
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
        del _players_in_game[interaction.user.name]
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

        await interaction.response.send_message(
            '<@' + str(interaction.user.id) +'> is now hosting a match!', 
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
        del _players_in_game[interaction.user.name]
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
        del _players_in_game[interaction.user.name]
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
        del _players_in_game[interaction.user.name]
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
        

            del _players_in_game[interaction.user.name]
            self.clear_items()
            await interaction.response.edit_message(content=interaction.user.name+' canceled the match!', view=self)
    
    
class JoinGame(discord.ui.View):
    """View for joining a game."""
    matching_embed: MatchMakeEmbed
    has_interacted_with: bool

    def __init__(self, match: Match, user: discord.User):
        super().__init__()
        self.has_interacted_with = False
        self.matching_embed = MatchMakeEmbed(match)

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
        elif interaction.user in self.matching_embed.match.players:
            await interaction.response.send_message('You are already in this match!', ephemeral=True)
        elif interaction.user.name in _players_in_game:
            await interaction.response.send_message('You are already in a match!', ephemeral=True)
        else:
            _players_in_game[interaction.user.name] = True
            self.matching_embed.match.add_player(interaction.user, int(get_player_data_from_json_file(interaction.user, interaction.guild.id)["ELO"]))
            self.matching_embed = MatchMakeEmbed(self.matching_embed.match)
            await interaction.response.edit_message(content='<@' + str(interaction.user.id) +'> is now hosting a match!', embed=self.matching_embed.get_embed(), view=self)
            # await interaction.response.send_message(interaction.user.name+' joined the match!', ephemeral=False)

    @button(label='Leave', style=discord.ButtonStyle.danger, custom_id="leave_button")
    async def leave_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        if interaction.user.id == self.matching_embed.get_host().id:
            await interaction.response.send_message('You can\'t leave your own match!', ephemeral=True)
        elif interaction.user.name not in _players_in_game:
            await interaction.response.send_message('You are not in a match!', ephemeral=True)
        elif interaction.user not in self.matching_embed.match.players:
            await interaction.response.send_message('You are not in this match!', ephemeral=True)
        else:
            del _players_in_game[interaction.user.name]
            _games_running[self.matching_embed.match.id].remove_player(interaction.user)
            self.matching_embed = MatchMakeEmbed(self.matching_embed.match)
            await interaction.response.edit_message(content='<@' + str(interaction.user.id) +'> is now hosting a match!', embed=self.matching_embed.get_embed(), view=self)
            # await interaction.response.send_message(interaction.user.name+' left the match!', ephemeral=False)

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
                del _players_in_game[player.name]
            del _games_running[self.matching_embed.match.id]
            await interaction.response.send_message(content="<@" + str(interaction.user.id)+'> cancelled the match!', view=self)


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
                },
                "elo_distribution": {
                    0: ("Stone", "aaaaaa", 35, -5, "N/A", 15, 10, 5), 
                    100: ("Iron", "ffffff", 35, -10, "N/A", 15, 10, 5),
                    200: ("Gold", "ffaa00", 30, -10, "N/A", 15, 10, 5),
                    300: ("Diamond", "55ffff", 25, -15, "N/A", 10, 5, 0),
                    400: ("Emerald", "00aa00", 25, -20, "N/A", 10, 5, 0),
                    500: ("Sapphire", "00aaaa", 20, -20, "N/A", 10, 5, 0),
                    600: ("Ruby", "aa0000", 15, -20, "N/A", 10, 5, 0),
                    700: ("Crystal", "ff55ff", 15, -25, "N/A", 5, 0, 0),
                    800: ("Opal", "5555ff", 10, -25, "N/A", 5, 0, 0),
                    900: ("Amethyst", "aa00aa", 10, -30, "N/A", 5, 0, 0),
                    1000: ("Rainbow", "0000ff", 10, -30, "N/A", 0, 0, 0)

                    # 0,Stone,aaaaaa,35,-5,N/A,15,10,5
                    # 100,Iron,ffffff,35,-10,N/A,15,10,5
                    # 200,Gold,ffaa00,30,-10,N/A,15,10,5
                    # 300,Diamond,55ffff,25,-15,N/A,10,5,
                    # 400,Emerald,00aa00,25,-20,N/A,10,5
                    # 500,Sapphire,00aaaa,20,-20,N/A,10,5
                    # 600,Ruby,aa0000,15,-20,N/A,10,5
                    # 700,Crystal,ff55ff,15,-25,N/A,5,,
                    # 800,Opal,5555ff,10,-25,N/A,5,,
                    # 900,Amethyst,aa00aa,10,-30,N/A,5,,
                    # 1000,Rainbow,0000ff,10,-30,N/A,,,
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
    return player not in _players_in_game


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
            players = {player: host_data["ELO"]}
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
                match_object = Match(match_id, todays_date, max_players, players, map, is_big_team_map, player, _players_in_game)
                _games_running[match_id] = match_object
                return match_object
    except Exception as e:
        print("Error creating match.")
        print(e)
        return None
    

def setup_elo_roles(guild_id: int) -> bool:
    """Sets up the ELO roles in the server. Returns True if successful, False otherwise."""
    try:
        with open("elo-distribution.txt", 'r') as file:
            for line in file:
                strs = line.split(",")
                if strs[0] == "Level":
                    continue
                # Check if the role already exists
                if strs[5] != "N/A":
                    # Check if the role exists
                    pass
                else:
                    # Create the role
                    pass
            file.close()
            return True
    except Exception as e:
        print(e)
        print("Error getting ELO distribution from file; please make sure you've modified it appropriately.\n \
              If not, the original template can be retrieved from https://github.com/jaronfernandes/casual-ranked-bedwars.")
        return False
    

def get_elo_distribution(guild_id: int) -> dict:
    """Return a dictionary of the ELO distribution, from lowest to highest."""
    try:
        with open("data", 'r') as file:
            string = file.read()
            data = json.loads(string)
            # check if guild exists
            if str(guild_id) not in data["SERVERS"]:
                setup_guild_in_json_file(guild_id)
                print(f"Created new server {guild_id} in data file.")
                with open("data", "r") as file:
                    string = file.read()
                    data = json.loads(string)

            print(data["SERVERS"][str(guild_id)]["elo_distribution"])

            return data["SERVERS"][str(guild_id)]["elo_distribution"]
    except Exception as e:
        print(e)
        print("Error occurred")
        return None
    

def get_admin_role(guild_id: int) -> str:
    """Return the admin role ID for a guild."""
    try:
        with open("data", 'r') as file:
            string = file.read()
            data = json.loads(string)
            # check if guild exists
            if str(guild_id) not in data["SERVERS"]:
                setup_guild_in_json_file(guild_id)
                print(f"Created new server {guild_id} in data file.")
                with open("data", "r") as file:
                    string = file.read()
                    data = json.loads(string)

            return data["SERVERS"][str(guild_id)]["admin_roles_id"]
    except Exception as e:
        print(e)
        print("Error occurred")
        return None
    

def get_scorer_roles(guild_id: int) -> str:
    """Return the scorer roles ID for a guild."""
    try:
        with open("data", 'r') as file:
            string = file.read()
            data = json.loads(string)
            # check if guild exists
            if str(guild_id) not in data["SERVERS"]:
                setup_guild_in_json_file(guild_id)
                print(f"Created new server {guild_id} in data file.")
                with open("data", "r") as file:
                    string = file.read()
                    data = json.loads(string)

            return data["SERVERS"][str(guild_id)]["scorer_roles_ids"]
    except Exception as e:
        print(e)
        print("Error occurred")
        return None
        
    
def get_players_in_game() -> dict:
    """Return a dictionary of players in game."""
    return _players_in_game


def get_games_running() -> dict:
    """Return a dictionary of games running."""
    return _games_running