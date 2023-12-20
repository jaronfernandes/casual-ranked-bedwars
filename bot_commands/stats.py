from __future__ import annotations

import discord, os, json
from data_access import get_player_data_from_json_file
from datetime import date
from discord.ext import commands
from discord.ui import Button, button
from dotenv import load_dotenv


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_stats_embed(self, ctx):
        """Return an embed for the stats menu."""
        current_guild_id = ctx.guild.id

        if type(ctx) == discord.interactions.Interaction:
            author = ctx.user
        else:
            author = ctx.author

        user_data = get_player_data_from_json_file(author, current_guild_id)

        with open('data', 'r') as file:
            string = file.read()
            data = json.loads(string)

        user_data = data["SERVERS"][str(ctx.guild.id)]["user_data"]
        user_id = str(author.id)

        user_stats = user_data[user_id]

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
            f"{('Winstreak: ' + str(user_stats['Winstreak'])) : <5}" + "\t" + f'{"WLR: " + str(round(user_stats["Wins"] / max(1, (user_stats["Wins"] + user_stats["Losses"])) , 2)) + "%" : <40}' + "\t" + f'{"Games: " + str(user_stats["Wins"] + user_stats["Losses"]) : <40}'

        stats_embed.add_field(name=f"Season {str(data['SERVERS'][str(current_guild_id)]['current_season']['season'])} Statistics", value=stats_row_one, inline=True)
        stats_embed.add_field(value=stats_row_two, name="", inline=False)

        try:
            stats_embed.set_thumbnail(url=author.avatar)
        except Exception as e:
            print(e)
            print("Error getting user image embed.")
        return stats_embed
    
    @commands.hybrid_command(aliases = ['s', 'statistics'], brief = '')
    async def stats(self, ctx):
        """Display the map pool for the current season."""
        await ctx.send(embed=self.create_stats_embed(ctx))

async def setup(bot):
    await bot.add_cog(Stats(bot))
