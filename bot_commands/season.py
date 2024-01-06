import discord, json
from discord import app_commands
from discord.ext import commands
from data_access import get_guild_data_from_json_file


class Season(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_season_embed(self, current_guild: discord.Guild, data, season: int) -> discord.Embed:
        """Return an embed for the current season.
        
        Preconditions:
        - current_guild_id is the ID of the current guild.
        """        
        if season == 0 or season == data["current_season"]["season"]:
            chosen_season = data["current_season"]
            season = chosen_season["season"]
            start_date = chosen_season["start_date"]
            end_date = chosen_season["end_date"]
            banned_items = chosen_season["banned_items"]
            season_user_data = data["user_data"]
        else:
            chosen_season = data["previous_season_statistics"][str(season)]
            start_date = chosen_season["start_date"]
            end_date = chosen_season["end_date"]
            banned_items = chosen_season["banned_items"]
            season_user_data = chosen_season["user_data"]

        embed = discord.Embed(
            title= current_guild.name + " | Season " + str(season),
            description="Season " + str(season) + " started on " + start_date + (" and ended on " + end_date + "." if end_date != "N/A" else "."),
            # aqua colour
            color= 0x00ffff
        )

        plrs = []
        # get top players based on ELO below
        for player in season_user_data:
            plrs.append({
                "ID": player,
                "ELO": season_user_data[player]["ELO"]
                })
        top_players = sorted(plrs, key=lambda k: k["ELO"], reverse=True)[:10]

        count = 1

        embed.add_field(name="Top Players", value="", inline=False)

        for player in top_players:
            embed.add_field(name="", value=str(count) + '. <@' + str(player['ID']) + '>', inline=True)
            embed.add_field(name="", value="ELO: " + str(player["ELO"]), inline=True)
            embed.add_field(name="", value="", inline=True)
            count += 1

        embed.add_field(name="Banned Items", value=str("\n".join(banned_items)), inline=True)

        season_stats_str = \
            "Total Matches: " + str(chosen_season["total_games_played"]) + "\n"

        embed.add_field(name="Season Statistics", value=season_stats_str)

        try:
            embed.set_thumbnail(url=current_guild.icon)
        except Exception as e:
            print(e)
            print("Error getting guild image embed.")

        return embed

    @commands.hybrid_command(aliases = ['ssn', 'szn'], brief = 'season [int]', description = "View the current season")
    @app_commands.describe(season='Season # to display.')
    async def season(self, ctx, season: int = 0):
        """Display the map pool for the current season."""
        current_guild_id = ctx.guild.id

        data = get_guild_data_from_json_file(current_guild_id)

        current_season = data["current_season"]["season"]
        if season < 0:
            await ctx.reply(content="Negative seasons do not exist! Please choose a range from 1 to " + str(current_season) + ", or 0/omitted for the current season.", mention_author=True, ephemeral=True)
        elif season > current_season:
            await ctx.reply(content="Season " + str(season) + " has not started yet! Please choose a range from 1 to " + str(current_season) + ", 0/omitted for the current season.", mention_author=True, ephemeral=True)
        else:
            await ctx.reply(embed=self.create_season_embed(ctx.guild, data, season), mention_author=True, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Season(bot))
