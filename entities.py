from __future__ import annotations

import discord
from discord.ui import Button, button


## BASIC CLASSES


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
    players_in_game: dict[str: bool]
    is_big_team_map: bool
    is_ready: bool
    is_randomized_teams: bool
    is_randomized_captains: bool

    def __init__(self, id: int, date: str, max_players: int, players: dict[str: int], map: str, is_big_team_map: bool, host: discord.User, players_in_game: dict[str: bool]) -> None:
        """Initialize a new match."""
        self.id = id
        self.host = host
        self.date = date
        self.max_players = max_players
        self.players = players
        self.map = map
        self.players_in_game = players_in_game
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
        self.players_in_game[player] = True
        self.players[player] = player_elo

    def remove_player(self, player: str) -> None:
        """Remove a player from the match.
        
        Preconditions: player in self.players
        """
        del self.players_in_game[player]
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


## UI CLASSES
        

# class RandomizeCaptains(discord.ui.View):
#     match: Match
#     players_in_game: dict[str: bool]
#     has_interacted_with: bool

#     def __init__ (self, match: Match, players_in_game: dict[str: bool]) -> None:
#         super().__init__()
#         self.has_interacted_with = False
#         self.players_in_game = players_in_game
#         self.match = match

#     @button(label='Random', style=discord.ButtonStyle.primary, custom_id="randomize_button")
#     async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True


#         self.clear_items()

#         self.match.set_randomized_captains()
#         new_view = JoinGame(self.match, interaction.user)
#         embedy = new_view.get_embed()
#         filey = new_view.get_file()

#         await interaction.response.send_message(
#             '<@' + str(interaction.user.id) +'> is now hosting a match!', 
#             ephemeral=False, 
#             file=filey,
#             embed=embedy,
#             view=new_view)

#     @button(label='Highest ELO', style=discord.ButtonStyle.primary, custom_id="non_randomize_button")
#     async def non_randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True

#         self.clear_items()

#         self.match.set_randomized_captains(False)
#         new_view = JoinGame(self.match, interaction.user)
#         embedy = new_view.get_embed()
#         filey = new_view.get_file()

#         await interaction.response.send_message(
#             '<@' + str(interaction.user.id) +'> is now hosting a match!', 
#             ephemeral=False, 
#             file=filey,
#             embed=embedy,
#             view=new_view)

#     @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
#     async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True

#         self.clear_items()
#         del self.players_in_game[interaction.user.name]
#         await interaction.response.send_message(content='You canceled the match!', view=self)
    
# class RandomizeTeams(discord.ui.View):
#     match: Match
#     players_in_game: dict[str: bool]
#     has_interacted_with: bool

#     def __init__ (self, match: Match, players_in_game: dict[str: bool]) -> None:
#         super().__init__()
#         self.has_interacted_with = False
#         self.players_in_game = players_in_game
#         self.match = match
    
#     @button(label='Random', style=discord.ButtonStyle.primary, custom_id="randomize_button")
#     async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True

#         self.clear_items()

#         self.match.set_randomized_teams()
#         new_view = JoinGame(self.match, interaction.user)
#         embedy = new_view.get_embed()
#         filey = new_view.get_file()

#         await interaction.response.send_message(
#             '<@' + str(interaction.user.id) +'> is now hosting a match!', 
#             ephemeral=False, 
#             file=filey,
#             embed=embedy,
#             view=new_view)
                
#     @button(label='Custom', style=discord.ButtonStyle.primary, custom_id="non_randomize_button")
#     async def non_randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True

#         self.clear_items()

#         self.match.set_randomized_teams(False)
#         new_view = RandomizeCaptains(self.match)
#         await interaction.response.edit_message(content='Do you want to randomize team captains?', view=new_view)

#     @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
#     async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True

#         self.clear_items()
#         del self.players_in_game[interaction.user.name]
#         await interaction.response.send_message(content='You canceled the match!', view=self)

# class RandomizeMap(discord.ui.View):
#     has_interacted_with: bool
#     players_in_game: dict[str: bool]
#     max_players: int

#     def __init__(self, max_players: int, players_in_game: dict[str: bool]) -> None:
#         super().__init__()
#         self.has_interacted_with = False
#         self.players_in_game = players_in_game
#         self.max_players = max_players

#     @button(label='Random', style=discord.ButtonStyle.primary, custom_id="randomize_button")
#     async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True

#         self.clear_items()
#         match = create_match(interaction.user, interaction.guild.id, False, True, self.max_players)
#         new_view = RandomizeTeams(match)
#         await interaction.response.edit_message(content='Do you want to randomize teams?', view=new_view)

#     @button(label='Custom', style=discord.ButtonStyle.primary, custom_id="non_randomize_button")
#     async def non_randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True
        
#         self.clear_items()
#         match = create_match(interaction.user, interaction.guild.id, False, False, self.max_players)
#         new_view = RandomizeTeams(match)
#         await interaction.response.edit_message(content='Do you want to randomize teams?', view=new_view)

#     @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
#     async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True
        
#         self.clear_items()
#         del players_in_game[interaction.user.name]
#         await interaction.response.send_message(content='You canceled the match!', view=self)


# class UsingSmallerMaps(discord.ui.View):
#     has_interacted_with: bool
#     players_in_game: dict[str: bool]
#     max_players: int

#     def __init__(self, max_players: int, players_in_game: dict[str: bool]) -> None:
#         super().__init__()
#         self.has_interacted_with = False
#         self.players_in_game = players_in_game
#         self.max_players = max_players

#     @button(label='Yes', style=discord.ButtonStyle.primary, custom_id="yes_button")
#     async def yes_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True
        
#         new_view = RandomizeMap(self.max_players)
#         self.clear_items()
#         await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)

#     @button(label='No', style=discord.ButtonStyle.primary, custom_id="no_button")
#     async def no_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True
        
#         new_view = RandomizeMap(self.max_players)
#         self.clear_items()
#         await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)

#     @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
#     async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         self.has_interacted_with = True
        
#         self.clear_items()
#         del self.players_in_game[interaction.user.name]
#         await interaction.response.edit_message(content='You canceled the match!', view=self)


# class CreateMatch(discord.ui.View):
#     host: discord.User
#     players_in_game: dict[str: bool]
#     has_interacted_with: bool

#     def __init__(self, host: discord.User, players_in_game: dict[str: bool]) -> None:
#         super().__init__()
#         self.has_interacted_with = False
#         self.players_in_game = players_in_game
#         self.host = host

#     @button(label='2', style=discord.ButtonStyle.primary, custom_id="2_button")
#     async def second_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.host.id != interaction.user.id:
#             await interaction.response.send_message('You are not the host!', ephemeral=True)
#         else:
#             if self.has_interacted_with:
#                 await interaction.response.send_message('This message has expired!', ephemeral=True)
#                 return
            
#             self.has_interacted_with = True
        
#             new_view = UsingSmallerMaps(2)
#             # self.clear_items()
#             # await interaction.response.edit_message(content='Will you be using a 3s/4s map?', view=new_view)
#             await interaction.response.send_message('Will you be using a 3s/4s map?', ephemeral=True, view=new_view)

        
#     @button(label='4', style=discord.ButtonStyle.primary, custom_id="4_button")
#     async def fourth_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.host.id != interaction.user.id:
#             await interaction.response.send_message('You are not the host!', ephemeral=True)
#         else:
#             if self.has_interacted_with:
#                 await interaction.response.send_message('This message has expired!', ephemeral=True)
#                 return
        
#             self.has_interacted_with = True
        
#             new_view = UsingSmallerMaps(4)
#             # self.clear_items()
#             # await interaction.response.edit_message(content='Will you be using a 3s/4s map?', view=new_view)
#             await interaction.response.send_message('Will you be using a 3s/4s map?', ephemeral=True, view=new_view)
    
#     @button(label='6', style=discord.ButtonStyle.primary, custom_id="6_button")
#     async def sixth_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.host.id != interaction.user.id:
#             await interaction.response.send_message('You are not the host!', ephemeral=True)
#         else:
#             if self.has_interacted_with:
#                 await interaction.response.send_message('This message has expired!', ephemeral=True)
#                 return
        
#             self.has_interacted_with = True
        
        
#             new_view = RandomizeMap(6)
#             # self.clear_items()
#             # await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)
#             await interaction.response.send_message('Do you want to randomize your map?', ephemeral=True, view=new_view)

#     @button(label='8', style=discord.ButtonStyle.primary, custom_id="8_button")
#     async def eighth_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.host.id != interaction.user.id:
#             await interaction.response.send_message('You are not the host!', ephemeral=True)
#         else:
#             if self.has_interacted_with:
#                 await interaction.response.send_message('This message has expired!', ephemeral=True)
#                 return
        
#             self.has_interacted_with = True
        

#             new_view = RandomizeMap(8)
#             # self.clear_items()
#             # await interaction.response.edit_message(content='Do you want to randomize your map?', view=new_view)
#             await interaction.response.send_message('Do you want to randomize your map?', ephemeral=True, view=new_view)

#     @button(label='Cancel Match', style=discord.ButtonStyle.danger, custom_id="cancel_button")
#     async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.host.id != interaction.user.id:
#             await interaction.response.send_message('You are not the host!', ephemeral=True)
#         else:
#             if self.has_interacted_with:
#                 await interaction.response.send_message('This message has expired!', ephemeral=True)
#                 return
        
#             self.has_interacted_with = True
        

#             del self.players_in_game[interaction.user.name]
#             self.clear_items()
#             await interaction.response.edit_message(content=interaction.user.name+' canceled the match!', view=self)
    
    
# class JoinGame(discord.ui.View):
#     """View for joining a game."""
#     matching_embed: MatchMakeEmbed
#     players_in_game: dict[str: bool]
#     has_interacted_with: bool

#     def __init__(self, match: Match, user: discord.User, players_in_game: dict[str: bool]):
#         super().__init__()
#         self.has_interacted_with = False
#         self.players_in_game = players_in_game
#         self.matching_embed = MatchMakeEmbed(match, user)

#     def get_embed(self) -> discord.Embed:
#         """Return the embed."""
#         return self.matching_embed.get_embed()
    
#     def get_file(self) -> discord.File:
#         """Return the file."""
#         return self.matching_embed.get_file()

#     @button(label='Join', style=discord.ButtonStyle.primary, custom_id="join_button")
#     async def join_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         if interaction.user.id == self.matching_embed.get_host().id:
#             await interaction.response.send_message('You can\'t join your own match!', ephemeral=True)
#         else:
#             self.players_in_game[interaction.user.name] = True
#             self.matching_embed.match.add_player(interaction.user.name, int(get_player_data_from_json_file(interaction.user, interaction.guild.id)["ELO"]))
#             self.matching_embed.update_new_player(interaction.user)
#             await interaction.response.send_message(interaction.user.name+' joined the match!', ephemeral=False)

#     @button(label='Leave', style=discord.ButtonStyle.danger, custom_id="leave_button")
#     async def leave_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if self.has_interacted_with:
#             await interaction.response.send_message('This message has expired!', ephemeral=True)
#             return
        
#         if interaction.user.id == self.matching_embed.get_host().id:
#             await interaction.response.send_message('You can\'t leave your own match!', ephemeral=True)
#         else:
#             del self.players_in_game[interaction.user.name]
#             games_running[self.matching_embed.match.id].remove_player(interaction.user.name)
#             self.matching_embed.remove_player(interaction.user)
#             await interaction.response.send_message(interaction.user.name+' left the match!', ephemeral=False)

#     @button(label='Cancel', style=discord.ButtonStyle.danger, custom_id="cancel_match_button")
#     async def cancel_match(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if interaction.user.id != self.matching_embed.get_host().id:
#             await interaction.response.send_message('You are not the host!', ephemeral=True)
#         else:
#             if self.has_interacted_with:
#                 await interaction.response.send_message('This message has expired!', ephemeral=True)
#                 return
        
#             self.has_interacted_with = True

#             self.clear_items()
#             for player in self.matching_embed.match.players:
#                 del self.players_in_game[player]
#             del games_running[self.matching_embed.match.id]
#             await interaction.response.send_message(content="<@" + str(interaction.user.id)+'> cancelled the match!', view=self)