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
    players: dict[discord.User: int]
    teams: dict[str: list[discord.User]]
    map: str
    players_in_game: dict[discord.User: bool]
    is_big_team_map: bool
    is_ready: bool
    is_randomized_teams: bool
    is_randomized_captains: bool

    def __init__(self, id: int, date: str, max_players: int, players: dict[discord.User: int], map: str, is_big_team_map: bool, host: discord.User, players_in_game: dict[str: bool]) -> None:
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

    def get_players(self) -> dict[discord.User: int]:
        """Return the players in the match."""
        return self.players
    
    def get_players_and_elo(self) -> dict[discord.User: int]:
        """Return the players along with their ELO in the match."""
        return self.players
    
    def get_max_players(self) -> int:
        """Return the maximum number of players in the match."""
        return self.max_players
    
    def get_randomized_teams(self) -> bool:
        """Return whether the match has randomized teams."""
        return self.is_randomized_teams
    
    def get_randomized_captains(self) -> bool:
        """Return whether the match has randomized captains."""
        return self.is_randomized_captains
    
    def get_teams(self) -> dict[str: list[discord.User]]:
        """Return the teams in the match."""
        return self.teams

    def player_in_match(self, player: discord.User) -> bool:
        """Return whether player is in the match."""
        return player in self.players

    def add_player(self, player: discord.User, player_elo: int) -> None:
        """Add a player to the match.
        
        Preconditions: player not in self.players
        """
        self.players_in_game[player] = True
        self.players[player] = player_elo

    def remove_player(self, player: discord.User) -> None:
        """Remove a player from the match.
        
        Preconditions: player in self.players
        """
        del self.players_in_game[player]
        del self.players[player]

    def is_full(self) -> bool:
        """Return whether the match is full."""
        return len(self.players) == self.max_players

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

    def __init__(self, match: Match):
        super().__init__()
        self.title = f"New Casual Ranked Bedwars Match {match.id}"
        self.match = match
        self.img_file = None
        self.players = self.match.get_players().keys()
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
    
    def set_teams(self, teams: dict[str, list[str]]) -> None:
        """Set the teams of the match."""
        self.teams = teams


class TeamMakeEmbed():
    match: Match
    title: str
    players: list[discord.User]
    img_file: discord.File
    embed: discord.Embed

    def __init__(self, match: Match):
        super().__init__()
        self.title = f"New Casual Ranked Bedwars Match {match.id}"
        self.match = match
        self.img_file = None
        self.players = self.match.get_players()
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

        # settings_str = \
        #     "Randomized Teams: " + ("Enabled" if self.match.get_randomized_teams() else "Disabled") + "\n" + \
        #     "Randomized Captains: " + ("Enabled" if self.match.get_randomized_captains() else "Disabled") + "\n" + \
        #     "Max Players: " + str(self.match.get_max_players()) + "\n" 
            
        captains_str = \
            "Team One Captain: <@" + str(self.match.teams["Team One"][0].id) + ">\n" + \
            "Team Two Captain: <@" + str(self.match.teams["Team Two"][0].id) + ">\n"
            
        team_one_str, team_two_str = "", ""
        
        for player in self.match.teams["Team One"]:
            team_one_str += "<@"+ str(player.id) + ">, "

        for player in self.match.teams["Team Two"]:
            team_two_str += "<@"+ str(player.id) + ">, "

        team_one_str = team_one_str.removesuffix(", ")
        team_two_str = team_two_str.removesuffix(", ")

        self.embed.add_field(name="Captains", value=captains_str, inline=False)
        self.embed.add_field(name="Team 1", value=team_one_str, inline=True)
        self.embed.add_field(name="Team 2", value=team_two_str, inline=True)


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
