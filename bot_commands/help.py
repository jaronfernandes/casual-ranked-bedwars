import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_help_embed(self, ctx):
        """Return an embed for the help menu."""
        help_embed = discord.Embed(
            title="Casual Ranked Bedwars Help Menu",
            description="Use Slash (/) Interactions or the prefix ! to execute commands.",
            # colour white
            color=0xffffff
        )

        help_embed.add_field(name="help", value="View the help menu.", inline=False)
        help_embed.add_field(name="play", value="Start a new game.", inline=False)
        help_embed.add_field(name="stats", value="Get your current season statistics.", inline=False)
        help_embed.add_field(name="season", value="View the current season.", inline=False)
        help_embed.add_field(name="rules", value="View the rules and instructions for Casual Ranked Bedwars.", inline=False)
        help_embed.add_field(name="maps", value="View the maps currently in rotation.", inline=False)
        help_embed.add_field(name="lb", value="View the leaderboard.", inline=False)
        help_embed.add_field(name="winners", value="View the winners of the previous season.", inline=False)
        help_embed.add_field(name="admin [command]", value="All admin commands (default displays a list of admin commands)", inline=False)

        try:
            help_embed.set_thumbnail(url=ctx.guild.icon)
        except Exception as e:
            print(e)
            print("Error getting guild image embed.")
        return help_embed

    @commands.hybrid_command(aliases = ['h'], brief = 'View the help menu')
    async def help(self, ctx):
        """Display the map pool for the current season."""
        await ctx.reply(embed=self.create_help_embed(ctx), ephemeral=True, mention_author=True)

async def setup(bot):
    await bot.add_cog(Help(bot))
