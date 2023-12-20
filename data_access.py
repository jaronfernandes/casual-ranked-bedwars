import discord, os, json, random
from datetime import date
from entities.entities import Match, MatchMakeEmbed


games_running = {}
players_in_game = {}


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