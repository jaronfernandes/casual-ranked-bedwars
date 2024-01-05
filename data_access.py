import discord, os, json, random
from datetime import date
from entities import Match, MatchMakeEmbed, TeamMakeEmbed
from discord.ui import button, select
from matchmaking import matchmake


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

        self.match.set_randomized_teams(False)
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

        if self.max_players == 2:
            match.set_randomized_teams()
            new_view = JoinGame(match, interaction.user)
            embedy = new_view.get_embed()
            filey = new_view.get_file()

            await interaction.response.send_message(
                '<@' + str(interaction.user.id) +'> is now hosting a match!', 
                ephemeral=False, 
                file=filey,
                embed=embedy,
                view=new_view)
        else:
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
            if self.matching_embed.match.is_full():
                self.clear_items()
                self.has_interacted_with = True
                
                # IF IT'S A 2 PLAYER GAME OR RANDOM, THEN GO STRAIGHT TO SCORING VIEW. OTHERWISE GO TO MATCH MAKE VIEW.
                if self.matching_embed.match.get_randomized_teams() or self.matching_embed.match.get_max_players() == 2:
                    remaining_players, teams_so_far = matchmake(self.matching_embed.match)
                    captains = [teams_so_far["Team One"][0], teams_so_far["Team Two"][0]]
                    self.matching_embed.match.set_teams(teams_so_far)

                    new_embed = TeamMakeEmbed(self.matching_embed.match)
                    # new_view = ScoringView(self.matching_embed.match, interaction.user)
                    new_view = MatchMakeView(self.matching_embed.match, captains[0].id, interaction.user, teams_so_far, remaining_players)
                    await interaction.response.edit_message(content='The match is now full!', embed=new_embed.get_embed(), view=self) # view=new_view
                else:
                    print("here")
                    remaining_players, teams_so_far = matchmake(self.matching_embed.match)
                    captains = [teams_so_far["Team One"][0], teams_so_far["Team Two"][0]]
                    self.matching_embed.match.set_teams(teams_so_far)

                    new_embed = TeamMakeEmbed(self.matching_embed.match)
                    new_view = MatchMakeView(self.matching_embed.match, captains[0].id, interaction.user, teams_so_far, remaining_players)
                    await interaction.response.edit_message(content="It is now <@" + str(captains[0].id) + ">'s turn to choose!", view=new_view, embed=new_embed.get_embed())
            else:
                await interaction.response.edit_message(embed=self.matching_embed.get_embed(), view=self)
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
            await interaction.response.edit_message(embed=self.matching_embed.get_embed(), view=self)
            # await interaction.response.send_message(interaction.user.name+' left the match!', ephemeral=False)

    @button(label='Cancel', style=discord.ButtonStyle.danger, custom_id="cancel_match_button")
    async def cancel_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.matching_embed.get_host().id:  # and not interaction.user.guild_permissions.administrator: # POTENTIALLY ADD THIS FOR ADMINS
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


def MatchMakeView(match: Match, captain_choosing: int, user: discord.User, teams: dict[str, list[discord.User]], players_remaining: list[discord.User]) -> discord.ui.View:
    """Return a MatchMakeView."""
    options_list = [discord.SelectOption(label=player.name.lower(), value=player.id) for player in players_remaining]
    print("HIIII")
    print(options_list)

    # Test options list: [discord.SelectOption(label="hi",value="hii")]

    class _MatchMakeView(discord.ui.View):
        """View for joining a game."""
        match: Match
        captains: list[discord.User]
        captain_choosing: int  # By ID, or -1 if no one is choosing.
        players_remaining: list[discord.User]
        options: list[discord.SelectOption]
        teams: dict[str, list[discord.User]]
        teams_embed: TeamMakeEmbed
        has_interacted_with: bool

        def __init__(self, match: Match, captain_choosing: int, user: discord.User, teams: dict[str, list[discord.User]], players_remaining: list[discord.User]):
            super().__init__()
            self.has_interacted_with = False
            self.match = match
            self.teams = teams
            self.captains = [teams["Team One"][0], teams["Team Two"][0]]
            self.captain_choosing = self.captains[0].id if captain_choosing == -1 else captain_choosing
            self.players_remaining = players_remaining
            self.options = options_list
            self.teams_embed = TeamMakeEmbed(match)
            

        def get_embed(self) -> discord.Embed:
            """Return the embed."""
            return self.matching_embed.get_embed()
        
        def get_file(self) -> discord.File:
            """Return the file."""
            return self.matching_embed.get_file()
        
        def get_options(self) -> list[discord.SelectOption]:
            """Return the options."""
            return self.options
        
        @select(placeholder='Select a player', options=options_list, custom_id="select_player")
        async def select_player(self, interaction: discord.Interaction, select: discord.ui.Select):
            if interaction.user.id != self.captains[0].id and interaction.user.id != self.captains[1].id:
                await interaction.response.send_message('You are not a captain!', ephemeral=True)
            elif interaction.user.id != self.captain_choosing:
                await interaction.response.send_message('It is not your turn to choose!', ephemeral=True)
            else:
                if self.has_interacted_with:
                    await interaction.response.send_message('This message has expired!', ephemeral=True)
                    return
            
                self.has_interacted_with = True

                player_chosen = interaction.guild.get_member(int(select.values[0]))
                print(player_chosen)
                self.players_remaining.remove(player_chosen)
                if self.captain_choosing == self.captains[0].id:
                    self.teams["Team One"].append(player_chosen)
                    self.captain_choosing = self.captains[1].id
                else:
                    self.teams["Team Two"].append(player_chosen)
                    self.captain_choosing = self.captains[0].id

                match = self.teams_embed.match
                match.set_teams(self.teams_embed.match.teams)

                if len(self.players_remaining) == 1:
                    # Even teams by default
                    self.teams["Team Two"].append(self.players_remaining[0])
                    match.set_teams(self.teams)
                    match.set_ready()
                    teams_embed = TeamMakeEmbed(self.match)
                    new_view = ScoringView(self.match, interaction.user, teams_embed.match.teams)
                    self.clear_items()
                    print([player.name for player in self.match.teams["Team One"]])
                    print([player.name for player in self.match.teams["Team Two"]])
                    await interaction.response.edit_message(content="The teams are now ready!", view=self, embed=teams_embed.get_embed())
                    return

                teams_embed = TeamMakeEmbed(self.match)
                new_view = MatchMakeView(self.match, self.captain_choosing, interaction.user, teams_embed.match.teams, teams_embed.match.players)
                await interaction.response.edit_message(content="It is now <@" + str(self.captain_choosing) + ">'s turn to choose", view=new_view, embed=teams_embed.get_embed())

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
                    del get_players_in_game[player.name]
                del get_games_running[self.matching_embed.match.id]
                await interaction.response.send_message(content="<@" + str(interaction.user.id)+'> cancelled the match!', view=self)
    
    return _MatchMakeView(match, captain_choosing, user, teams, players_remaining)

class ScoringView(discord.ui.View):
    """View for scoring a game."""
    match: Match
    teams: dict[str, list[discord.User]]
    TeamMakeEmbed: TeamMakeEmbed
    has_interacted_with: bool

    def __init__(self, match: Match, user: discord.User, teams: dict[str, list[discord.User]]):
        super().__init__()
        self.has_interacted_with = False
        self.match = match
        self.teams = teams
        self.matching_embed = TeamMakeEmbed(match)
        

    def get_embed(self) -> discord.Embed:
        """Return the embed."""
        return self.matching_embed.get_embed()
    
    def get_file(self) -> discord.File:
        """Return the file."""
        return self.matching_embed.get_file()
    
    @button(label='Score', style=discord.ButtonStyle.green, custom_id="score_button")
    async def score_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:  ## ADD SCORER ROLE HERE IN THE FUTURE.
            await interaction.response.send_message('You are not an administrator!', ephemeral=True)
        else:
            if self.has_interacted_with:
                await interaction.response.send_message('This message has expired!', ephemeral=True)
                return

            self.has_interacted_with = True

            self.clear_items()
            self.match.set_ready()
            teams_embed = TeamMakeEmbed(self.match)
            new_view = ScoringView(self.match, interaction.user, teams_embed.match.teams)
            await interaction.response.edit_message(content="The teams are now ready!", view=self)
    
    @button(label='Cancel', style=discord.ButtonStyle.danger, custom_id="cancel_match_button")
    async def cancel_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('You are not an administrator!', ephemeral=True)
        else:
            if self.has_interacted_with:
                await interaction.response.send_message('This message has expired!', ephemeral=True)
                return
        
            self.has_interacted_with = True

            self.clear_items()
            for player in self.matching_embed.match.players:
                del get_players_in_game[player.name]
            del get_games_running[self.matching_embed.match.id]
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
                # setup_elo_roles(guild_id)


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

            # FUTURE CODE FOR SCORING A USER FOR THE FIRST TIME.    

            # elo_dict = get_elo_distribution(current_guild_id)
            # # convert each key to an integer, and then sort
            # lowest_role = sorted([int(key) for key in elo_dict])[0]
            # if all(lowest_role.id != role.id for role in player.roles):
            #     # Give the player the lowest role
            #     # Only have guild id. Need to get the guild object from it! and bot.get_guild doesn't work since we're in the wrong file!
            #     guild = discord.utils.get(player.guilds, id=current_guild_id)
            #     role = await guild.get_role(lowest_role.id)
            #     await player.add_roles(role)


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


def get_guild_data_from_json_file(guild_id: int) -> dict:
    """Return a dictionary of guild data from a file.
    
    Preconditions:
    - guild_id is a valid Discord guild ID.
    """
    try:
        with open("data", "r") as file:
            string = file.read()
            data = json.loads(string)
            # check if guild doesn't exist
            if str(guild_id) not in data["SERVERS"]:
                setup_guild_in_json_file(guild_id)
                print(f"Created new server {guild_id} in data file.")
                with open("data", "r") as file:
                    string = file.read()
                    data = json.loads(string)

            return data["SERVERS"][str(guild_id)]
    except Exception as e:
        print(e)
        print("Error getting guild data from file! Please submit an issue to https://github.com/jaronfernandes/casual-ranked-bedwars.")
        

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
    

def backup_data() -> bool:
    """Backup the data file."""
    try:
        with open(f"data", "r") as file:
            string = file.read()
            data = json.loads(string)

            with open(f"backup_data_{str(date.today())}.json", "w") as backup_file:
                json.dump(data, backup_file)
                return True
    except Exception as e:
        print(e)
        print("Error backing up data.")
        return False
    

def clear_data() -> bool:
    """Clear the data file."""
    try:
        with open("data", "w") as file:
            data = {
                "warning_msg": "DO NOT MODIFY THIS FILE; THESE ARE HANDLED BY THE BOT",
                "SERVERS": {}
            }
            json.dump(data, file)
            return True
    except Exception as e:
        print(e)
        print("Error clearing data.")
        return False
    

def reset_season(guild_id: int) -> bool:
    """Reset the season for a guild."""
    try:
        with open("data", "r") as file:
            string = file.read()
            data = json.loads(string)

            data["SERVERS"][str(guild_id)]["previous_season_statistics"][str(data["SERVERS"][str(guild_id)]["current_season"]["season"])] = {
                "user_data": data["SERVERS"][str(guild_id)]["user_data"],
                "total_games_played": data["SERVERS"][str(guild_id)]["current_season"]["total_games_played"],
                "start_date": data["SERVERS"][str(guild_id)]["current_season"]["start_date"],
                "end_date": str(date.today())
            }

            new_season_number = data["SERVERS"][str(guild_id)]["current_season"]["season"] + 1

            data["SERVERS"][str(guild_id)]["current_season"] = {
                "season": new_season_number,
                "total_games_played": 0,
                "start_date": str(date.today()),
                "end_date": "N/A",
                "banned_items": ["Knockback Stick", "Pop-up Towers", "Obsidian", "Punch Bows"]
            }

            data["SERVERS"][str(guild_id)]["games_played"] = 0
            data["SERVERS"][str(guild_id)]["user_data"] = {}

            with open("data", "w") as jsonFile:
                json.dump(data, jsonFile)
                return (True, new_season_number)
    except Exception as e:
        print(e)
        print("Error resetting season.")
        return (False, -1)


async def setup_elo_roles(guild: discord.Guild) -> bool:
    """Sets up the ELO roles in the server (through the DATA FILE!). Returns True if successful, False otherwise."""
    # try:
    elo_distribution = get_elo_distribution(guild.id)
    with open("elo-distribution.txt", 'r') as file:
        file_cpy = ""

        for line in file:
            strs = line.split(",")
            if strs[0] == "Level":
                file_cpy += line
                continue
            # Check if the role already exists
            if strs[5] != "N/A":
                # Check if the role exists
                if int(strs[5]) in [role.id for role in guild.roles]:
                    # Update the role
                    role = guild.get_role(int(strs[5]))
                    # print(role.color.value, int(strs[2], 16))
                    if role.colour.value != int(strs[2], 16):
                        # Update the role colour
                        await role.edit(colour=discord.Colour(int(strs[2], 16)))
                else:
                    # Create the role and UPDATE the new txt file with the ID.
                    role = await guild.create_role(name=strs[1], colour=discord.Colour(int(strs[2], 16)))
            else:
                # Create the role
                role = await guild.create_role(name=strs[1], colour=discord.Colour(int(strs[2], 16)))

            file_cpy += ",".join([strs[0], strs[1], strs[2], strs[3], strs[4], str(role.id), strs[6], strs[7], strs[8]])
        # Update the file
        file.close()

        with open("elo-distribution.txt", 'w') as file:
            file.write(file_cpy)

        file.close()

        setup_elo_distribution()
        return True
    # except Exception as e:
    print(e)
    print("Error getting ELO distribution from file; please make sure you've modified it appropriately.\n \
            If not, the original template can be retrieved from https://github.com/jaronfernandes/casual-ranked-bedwars.")
    return False


def setup_elo_distribution() -> None:
    """Set up the ELO distribution from the txt file."""
    with open("data", 'r') as file:
        string = file.read()
        data = json.loads(string)
        for guild_id in data["SERVERS"]:
            elo_distribution = {}
            with open("elo-distribution.txt", 'r') as file:
                for line in file:
                    strs = line.split(",")
                    if strs[0] == "Level":
                        continue
                    elo_distribution[int(strs[0])] = (strs[1], strs[2], int(strs[3]), int(strs[4]), strs[5], int(strs[6]), int(strs[7]), int(strs[8]))
                file.close()
            data["SERVERS"][guild_id]["elo_distribution"] = elo_distribution
            with open("data", "w") as jsonFile:
                json.dump(data, jsonFile)
            jsonFile.close()
        file.close()


async def delete_elo_roles(guild: discord.Guild) -> None:
    """Delete the ELO roles from the server."""
    with open("elo-distribution.txt", 'r') as file:

        for line in file:
            strs = line.split(",")
            if strs[0] == "Level":
                continue
            # Check if the role already exists
            if strs[5] != "N/A":
                # Check if the role exists
                if strs[5] in [role.id for role in guild.roles]:
                    # Delete the role
                    role = guild.get_role(strs[5])
                    await role.delete()

        # Update the file
        file.close()

        setup_elo_distribution()
    

def get_elo_distribution(guild_id: int) -> dict:
    """Return a dictionary of the CURRENT ELO distribution from json file, NOT the txt file, from lowest to highest."""
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
