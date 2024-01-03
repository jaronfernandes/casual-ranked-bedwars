from __future__ import annotations

import discord, os, json
from data_access import get_player_data_from_json_file, get_guild_data_from_json_file
from datetime import date
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, button
from dotenv import load_dotenv


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_stats_embed(self, ctx, user: discord.Member = None) -> discord.Embed:
        """Return an embed for the stats menu."""
        current_guild_id = ctx.guild.id

        if user is not None:
            if type(ctx) == discord.interactions.Interaction:
                author = ctx.user
            else:
                author = ctx.author
            if user.id != author.id:
                author = user

        elif type(ctx) == discord.interactions.Interaction:
            author = ctx.user
        else:
            author = ctx.author

        print(author.name)

        data = get_guild_data_from_json_file(current_guild_id)
        user_stats = get_player_data_from_json_file(author, current_guild_id)

        stats_embed = discord.Embed(
            title=f"{author.name}'s Overall Stats" ,
            # colour orange
            color=0xffa500
        )
        # {(str(count) + '. <@' + str(player['ID']) + '>') : <30}
        stats_row_one = \
            f'{"ELO: " + str(user_stats["ELO"]) : <40}' + "\t" + f'{"Wins: " + str(user_stats["Wins"]) : <40}' + "\t" + f'{"Losses: " + str(user_stats["Losses"]) : <40}'
            # "ELO: " + str(user_stats["ELO"]) + "\n" + \
            # "Wins: " + str(user_stats["Wins"]) + "\n" + \
            # "Losses: " + str(user_stats["Losses"]) + "\n"
        
        stats_row_two = \
            f"{('Winstreak: ' + str(user_stats['Winstreak'])) : <5}" + "\t" + f'{"WLR: " + str(100 * round(user_stats["Wins"] / max(1, (user_stats["Wins"] + user_stats["Losses"])) , 4)) + "%" : <40}' + "\t" + f'{"Games: " + str(user_stats["Wins"] + user_stats["Losses"]) : <40}'

        stats_embed.add_field(name=f"Season {str(data['current_season']['season'])} Statistics", value=stats_row_one, inline=True)
        stats_embed.add_field(value=stats_row_two, name="", inline=False)

        try:
            stats_embed.set_thumbnail(url=author.avatar)
        except Exception as e:
            print(e)
            print("Error getting user image embed.")
        return stats_embed
    
    @commands.hybrid_command(aliases = ['s', 'statistics'], brief = "stats [DISCORD USERNAME] (default yours)", description = "View your stats or another player's stats.")
    @app_commands.describe(username='Discord username of the player to view stats for.')
    async def stats(self, ctx, username=None):
        """Display the map pool for the current season."""        
        if username is None:
            await ctx.send(embed=self.create_stats_embed(ctx))
            return
        
        member_to_get_stats = ctx.guild.get_member_named(username)
        
        if member_to_get_stats is None:
            await ctx.send("Please enter a valid username from this server!")
        else:
            await ctx.send(embed=self.create_stats_embed(ctx, member_to_get_stats))

async def setup(bot):
    await bot.add_cog(Stats(bot))
