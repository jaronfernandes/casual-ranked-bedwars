import discord
import json
import math
from discord import app_commands
from discord.ext import commands
from data_access import setup_guild_in_json_file


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_leaderboard_embed(self, ctx, data, stats: discord.app_commands.Choice[str], page: int) -> discord.Embed:
        """Return an embed for this season's leaderboard."""
        current_season = data["SERVERS"][str(ctx.guild.id)]["current_season"]['season']

        lb_embed = discord.Embed(
            title=f"Season {current_season} | {stats.name} Leaderboard",
            description=f"Page {page}",
            # colour magenta
            color=0xff00ff
        )

        guild_id = ctx.guild.id

        embed_field_value = ""

        if stats.value == "elo":
            embed_field_value = sorted(data["SERVERS"][str(guild_id)]["user_data"], key=lambda k: data["SERVERS"][str(guild_id)]["user_data"][k]["ELO"], reverse=True)[10 * (page - 1):10 * page]
        elif stats.value == "wins":
            embed_field_value = sorted(data["SERVERS"][str(guild_id)]["user_data"], key=lambda k: data["SERVERS"][str(guild_id)]["user_data"][k]["Wins"], reverse=True)[10 * (page - 1):10 * page]
        elif stats.value == "wlr":
            embed_field_value = sorted(data["SERVERS"][str(guild_id)]["user_data"], key=lambda k: data["SERVERS"][str(guild_id)]["user_data"][k]["Wins"] / max(1, data["SERVERS"][str(guild_id)]["user_data"][k]["Losses"]), reverse=True)[10 * (page - 1):10 * page]
        elif stats.value == "ws":
            embed_field_value = sorted(data["SERVERS"][str(guild_id)]["user_data"], key=lambda k: data["SERVERS"][str(guild_id)]["user_data"][k]["Winstreak"], reverse=True)[10 * (page - 1):10 * page]

        top_players_str = ""

        count = 1 + 10 * (page - 1)

        for player in embed_field_value:
            top_players_str += f"{(str(count) + '. <@' + str(player) + '>') : <30}"
            
            if stats.value == "elo":
                top_players_str += "\t ELO: " + str(data["SERVERS"][str(guild_id)]["user_data"][player]["ELO"]) + "\n"
            elif stats.value == "wins":
                top_players_str += "\t Wins: " + str(data["SERVERS"][str(guild_id)]["user_data"][player]["Wins"]) + "\n"
            elif stats.value == "wlr":
                top_players_str += "\t W/L Ratio: " + str(data["SERVERS"][str(guild_id)]["user_data"][player]["Wins"] / max(1, data["SERVERS"][str(guild_id)]["user_data"][player]["Losses"])) + "\n"
            elif stats.value == "ws":
                top_players_str += "\t Winstreak: " + str(data["SERVERS"][str(guild_id)]["user_data"][player]["Winstreak"]) + "\n"

            count += 1

        lb_embed.add_field(name="Top Players", value=top_players_str, inline=False)

        try:
            lb_embed.set_thumbnail(url=ctx.guild.icon)
        except Exception as e:
            print(e)
            print("Error getting guild image embed.")
        return lb_embed

    @commands.hybrid_command(aliases = ['lb'], brief = 'Displays the leaderboard current season.')
    @app_commands.describe(stats='Stat to display on the leaderboard.')
    @app_commands.choices(stats=[
        discord.app_commands.Choice(name="ELO", value="elo"),
        discord.app_commands.Choice(name="Wins", value="wins"),
        discord.app_commands.Choice(name="W/L Ratio", value="wlr"),
        discord.app_commands.Choice(name="Winstreak", value="ws"),
    ])
    @app_commands.describe(page='Page of the leaderboard to display.')
    async def leaderboard(self, ctx, stats: discord.app_commands.Choice[str], page: int = 1):
        """Display the map pool for the current season."""
        guild_id = ctx.guild.id

        with open("data", "r") as file:
            string = file.read()
            data = json.loads(string)

            if str(guild_id) not in data["SERVERS"]:
                setup_guild_in_json_file(guild_id)
                print(f"Created new server {guild_id} in data file.")
                with open("data", "r") as file:
                    string = file.read()
                    data = json.loads(string)
                    
        # Check if there are enough users for the page number.
        total_pages = math.ceil(len(data["SERVERS"][str(guild_id)]["user_data"]) / 10)
        if total_pages == 0:
            await ctx.send("There are no users in the database!")
        elif page > total_pages or page < 1:
            await ctx.send("Invalid page number! Please try a page number between 1 and " + str(total_pages) + ".")
        else:
            await ctx.send(embed=self.create_leaderboard_embed(ctx, data, stats, page))

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
