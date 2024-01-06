"""File for scoring matches."""
import discord


def _score_player(guild_id: int, player: discord.User, user_elo: int, killer_list: list[discord.User], elo_dict: dict, won: bool, interaction: discord.Interaction) -> int:
    """Return the gained ELO of a player in a match."""
    min_elo_user_needs, added_elo = 0, 0

    if player in killer_list:
        if player == killer_list[0]:
            added_elo = int(elo_dict[elo_indices[player]][5])
        elif player == killer_list[1]:
            added_elo = int(elo_dict[elo_indices[player]][6])
        else:
            added_elo = int(elo_dict[elo_indices[player]][7])

    for min_elo_key in elo_indices:
        if user_elo < min_elo_key and :
            elo_key = min_elo_key
            break



def scoring_algorithm(guild_id: int, scoring_data: dict, player_elos: dict, elo_dict: dict, interaction: discord.Interaction) -> dict[discord.User: (int, int)]:
    """Return the score and new/same role id of a player in a match."""
    killer_list = scoring_data["Top Killers"]
    new_elo_dict = {}

    for player in scoring_data["Winning Team"]:
        new_elo_dict[player] = _score_player(guild_id, player, player_elos[player], killer_list, elo_dict, True, interaction)

    for player in scoring_data["Losing Team"]:
        new_elo_dict[player] = _score_player(guild_id, player, player_elos[player], killer_list, elo_dict, False, interaction)

    return new_elo_dict
