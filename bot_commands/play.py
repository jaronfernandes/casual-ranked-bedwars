from __future__ import annotations

from data_access import valid_for_matchmaking, get_players_in_game, CreateMatch
from discord.ext import commands


class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(aliases = ['p', 'start'], brief = '')
    async def play(self, ctx):
        """Display the map pool for the current season."""
        if valid_for_matchmaking(ctx.author.name):
            get_players_in_game()[ctx.author.name] = True
            viewe = CreateMatch(ctx.author)
            await ctx.send(content="Enter the amount of players you'd like to play with with (2,4,6,8).", view=viewe)
        else:
            await ctx.send('You\'re already in a game!')

async def setup(bot):
    await bot.add_cog(Play(bot))
