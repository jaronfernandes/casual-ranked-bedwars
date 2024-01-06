"""File for scoring matches."""
import discord


def _get_role_by_elo(user_elo: int, elo_dict: dict) -> (int, int):
    """Return the role id of a player based on their elo."""
    elo = round(user_elo, -2)  # round to nearest 100th
    if user_elo < elo:  # In other cases, the rounding suffices.
        elo = elo - 100
    
    return (elo, int(elo_dict[str(elo)][4]))


def _score_player(guild_id: int, player: discord.User, user_elo: int, killer_list: list[discord.User], elo_dict: dict, won: bool, interaction: discord.Interaction) -> (int, int, int):
    """Return the gained ELO of a player in a match."""
    added_elo, current_role, role_to_get = 0, 0, 0

    elo_list = [(int(key), elo_dict[key]) for key in elo_dict]
    elo_list.sort(key=lambda x: x[0], reverse=True)
    
    elo, current_role = _get_role_by_elo(user_elo, elo_dict)

    if player in killer_list:
        if player == killer_list[0]:
            added_elo = int(elo_dict[str(elo)][5])
        elif player == killer_list[1]:
            added_elo = int(elo_dict[str(elo)][6])
        else:
            added_elo = int(elo_dict[str(elo)][7])

    if won:
        added_elo += int(elo_dict[str(elo)][2])
    else:
        added_elo += int(elo_dict[str(elo)][3])

    updated_elo = max(0, user_elo + added_elo)
    _, role_to_get = _get_role_by_elo(updated_elo, elo_dict)

    # Returns new elo, current role id, and the new role id to get.
    return (updated_elo, current_role, role_to_get)


def scoring_algorithm(guild_id: int, scoring_data: dict, player_elos: dict, elo_dict: dict, interaction: discord.Interaction) -> dict[discord.User: (int, int, int)]:
    """Return the score and same + new role id of a player in a match."""
    killer_list = scoring_data["Top Killers"]
    new_elo_dict = {}

    for player in scoring_data["Winning Team"]:
        new_elo_dict[player] = _score_player(guild_id, player, player_elos[player], killer_list, elo_dict, True, interaction)

    for player in scoring_data["Losing Team"]:
        new_elo_dict[player] = _score_player(guild_id, player, player_elos[player], killer_list, elo_dict, False, interaction)

    return new_elo_dict
