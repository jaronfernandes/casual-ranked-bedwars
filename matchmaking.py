import discord
from discord.ext import commands
from discord.ui import Button, button, select
from entities import Match, TeamMakeEmbed
import random


def _append_to_team(i: int, teams: dict[str, list[discord.User]], player: discord.User) -> None:
    """Helper function that adds a player to a team."""
    if i % 2 == 0:
        teams["Team One"].append(player)
    else:
        teams["Team Two"].append(player)


def matchmake(match: Match) -> tuple[list[discord.User], dict[str, list[discord.User]]]:
    """
    Returns a tuple of the remaining players, as well as the teams so far.
    """
    plrs = match.get_players()
    teams = {"Team One": [], "Team Two": []}
    total_players = len(plrs)
    plr_list = list(plrs.keys())


    if match.get_randomized_teams():
        # Randomized Teams
        for i in range(0, total_players):
            rand_index = random.randint(0, len(plr_list) - 1)
            chosen_user = plr_list[rand_index]

            _append_to_team(i, teams, chosen_user)

            plr_list.pop(rand_index)
            
            
    elif match.get_randomized_captains():
        # Randomized Captains, but they choose their teams
        for i in range(0, 2):
            rand_index = random.randint(0, len(plr_list) - 1)
            chosen_user = plr_list[rand_index]

            _append_to_team(i, teams, chosen_user)

            plr_list.pop(rand_index)
    else:
        # Based on highest ELO, returns 
        for i in range(0, total_players):
            highest_elo = 0
            second_highest_elo = 0
            players_with_highest_elo = []
            players_with_second_highest_elo = []

            for key in plrs:
                if plrs[key] > highest_elo:
                    second_highest_elo = highest_elo
                    players_with_second_highest_elo = players_with_highest_elo
                    highest_elo = plrs[key]
                    players_with_highest_elo = [key]
                elif plrs[key] == highest_elo:  # Tie
                    players_with_highest_elo.append(key)
                elif plrs[key] > second_highest_elo:
                    second_highest_elo = plrs[key]
                    players_with_second_highest_elo = [key]
                elif plrs[key] == second_highest_elo:  # Tie
                    players_with_second_highest_elo.append(key)
        if len(players_with_second_highest_elo) == 0:
            teams["Team One"].append(random.choice(players_with_highest_elo))
            plr_list.remove(teams["Team One"][0])
            
            teams["Team Two"].append(random.choice(players_with_highest_elo))
            plr_list.remove(teams["Team Two"][0])
        else:
            teams["Team One"].append(random.choice(players_with_second_highest_elo))  # So second highest ELO gets the first pick to make it more fair.
            teams["Team Two"].append(random.choice(players_with_highest_elo))

            plr_list.remove(teams["Team One"][0])
            plr_list.remove(teams["Team Two"][0])

    # Returns a tuple of the remaining players, as well as the teams so far.
    return (plr_list, teams) 
    

# class MatchMakeView(discord.ui.View):
#     """View for joining a game."""
#     match: Match
#     captains: list[discord.User]
#     captain_choosing: int  # By ID, or -1 if no one is choosing.
#     players_remaining: list[discord.User]
#     options: list[discord.SelectOption]
#     teams: dict[str, list[discord.User]]
#     teams_embed: TeamMakeEmbed
#     has_interacted_with: bool

#     def __init__(self, match: Match, captain_choosing: int, user: discord.User, teams: dict[str, list[discord.User]], players_remaining: list[discord.User]):
#         super().__init__()
#         self.has_interacted_with = False
#         self.match = match
#         self.teams = teams
#         self.captains = [teams["Team One"][0], teams["Team Two"][0]]
#         self.captain_choosing = self.captains[0].id if captain_choosing == -1 else captain_choosing
#         self.players_remaining = players_remaining
#         self.options = [discord.SelectOption(label=player.name, value=player.name) for player in players_remaining]
#         self.teams_embed = TeamMakeEmbed(match)
        

#     def get_embed(self) -> discord.Embed:
#         """Return the embed."""
#         return self.matching_embed.get_embed()
    
#     def get_file(self) -> discord.File:
#         """Return the file."""
#         return self.matching_embed.get_file()
    
#     def get_options(self) -> list[discord.SelectOption]:
#         """Return the options."""
#         return self.options
    
#     @select(placeholder='Select a player', options=get_options())
#     async def select_player(self, select: discord.ui.Select, interaction: discord.Interaction):
#         if interaction.user.id != self.captains[0].id and interaction.user.id != self.captains[1].id:
#             await interaction.response.send_message('You are not a captain!', ephemeral=True)
#         elif interaction.user.id != self.captain_choosing:
#             await interaction.response.send_message('It is not your turn to choose!', ephemeral=True)
#         else:
#             if self.has_interacted_with:
#                 await interaction.response.send_message('This message has expired!', ephemeral=True)
#                 return
        
#             self.has_interacted_with = True

#             player_chosen = select.values[0]
#             self.players_remaining.remove(player_chosen)
#             if self.captain_choosing == self.captains[0].id:
#                 self.teams["Team One"].append(player_chosen)
#                 self.captain_choosing = self.captains[1].id
#             else:
#                 self.teams["Team Two"].append(player_chosen)
#                 self.captain_choosing = self.captains[0].id

#             match = self.teams_embed.match
#             match.set_teams(self.teams_embed.match.teams)

#             if len(self.players_remaining) == 1:
#                 # Even teams by default
#                 self.teams["Team Two"].append(self.players_remaining[0])
#                 match.set_teams(self.teams)
#                 match.set_ready()
#                 teams_embed = TeamMakeEmbed(self.match)
#                 new_view = ScoringView(self.match, self.captain_choosing, interaction.user, teams_embed.match.teams, teams_embed.match.players)
#                 await interaction.response.edit_message(content="The teams are now ready!", view=self)
#                 return

#             teams_embed = TeamMakeEmbed(self.match)
#             new_view = MatchMakeView(self.match, self.captain_choosing, interaction.user, teams_embed.match.teams, teams_embed.match.players)
#             await interaction.response.edit_message(content="It is now <@" + self.captain_choosing + ">'s turn to choose", view=new_view, embed=teams_embed.get_embed())

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
#                 del get_players_in_game[player.name]
#             del get_games_running[self.matching_embed.match.id]
#             await interaction.response.send_message(content="<@" + str(interaction.user.id)+'> cancelled the match!', view=self)


# class ScoringView(discord.ui.View):
#     """View for scoring a game."""
#     match: Match
#     options: list[discord.SelectOption]
#     TeamMakeEmbed: TeamMakeEmbed
#     has_interacted_with: bool

#     def __init__(self, match: Match, user: discord.User):
#         super().__init__()
#         self.has_interacted_with = False
#         self.match = match
#         teams_so_far = matchmake(match)[1]
#         self.options = matchmake(match)[0]
#         self.matching_embed = TeamMakeEmbed(match)
        

#     def get_embed(self) -> discord.Embed:
#         """Return the embed."""
#         return self.matching_embed.get_embed()
    
#     def get_file(self) -> discord.File:
#         """Return the file."""
#         return self.matching_embed.get_file()
    
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
#                 del get_players_in_game[player.name]
#             del get_games_running[self.matching_embed.match.id]
#             await interaction.response.send_message(content="<@" + str(interaction.user.id)+'> cancelled the match!', view=self)
