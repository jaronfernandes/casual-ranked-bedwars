import discord
import json
import math
from discord import app_commands
from discord.ext import commands
from data_access import get_guild_data_from_json_file


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_leaderboard_embed(self, ctx, data, stats: discord.app_commands.Choice[str], page: int) -> discord.Embed:
        """Return an embed for this season's leaderboard."""
        current_season = data["current_season"]['season']

        lb_embed = discord.Embed(
            title=f"Season {current_season} | {stats.name} Leaderboard",
            description=f"Page {page}",
            # colour magenta
            color=0xff00ff
        )

        guild_id = ctx.guild.id

        embed_field_value = ""

        if stats.value == "elo":
            embed_field_value = sorted(data["user_data"], key=lambda k: data["user_data"][k]["ELO"], reverse=True)[10 * (page - 1):10 * page]
        elif stats.value == "wins":
            embed_field_value = sorted(data["user_data"], key=lambda k: data["user_data"][k]["Wins"], reverse=True)[10 * (page - 1):10 * page]
        elif stats.value == "wlr":
            embed_field_value = sorted(data["user_data"], key=lambda k: data["user_data"][k]["Wins"] / max(1, data["user_data"][k]["Losses"]), reverse=True)[10 * (page - 1):10 * page]
        elif stats.value == "ws":
            embed_field_value = sorted(data["user_data"], key=lambda k: data["user_data"][k]["Winstreak"], reverse=True)[10 * (page - 1):10 * page]

        count = 1 + 10 * (page - 1)
        lb_embed.add_field(name="Top Players by " + stats.name, value="", inline=False)

        for player in embed_field_value:
            prefix = f'{str(count)}. <@{player}>'
            
            if stats.value == "elo":
                base = "ELO: " + str(data['user_data'][player]['ELO'])
            elif stats.value == "wins":
                base = "Wins: " + str(data['user_data'][player]['Wins'])
            elif stats.value == "wlr":
                base = "W/L Ratio: " + str(round(data['user_data'][player]['Wins'] / max(1, data['user_data'][player]['Losses']), 2))
            elif stats.value == "ws":
                base = "Winstreak: " + str(data['user_data'][player]['Winstreak'])

            # invisible charcter for name below
            lb_embed.add_field(name="", value=prefix, inline=True)
            lb_embed.add_field(name="", value=base, inline=True)
            lb_embed.add_field(name="", value="", inline=True)

            count += 1

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

        data = get_guild_data_from_json_file(ctx.guild.id)
                    
        # Check if there are enough users for the page number.
        total_pages = math.ceil(len(data["user_data"]) / 10)
        if total_pages == 0:
            await ctx.reply(content="There are no users in the database!", mention_author=True, ephemeral=True)
        elif page > total_pages or page < 1:
            await ctx.reply(content="Invalid page number! Please try a page number between 1 and " + str(total_pages) + ".", mention_author=True, ephemeral=True)
        else:
            await ctx.reply(embed=self.create_leaderboard_embed(ctx, data, stats, page), mention_author=True, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
