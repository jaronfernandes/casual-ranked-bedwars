import discord
from discord.ext import commands


class Maps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_maps_embed(self, ctx):
        """Return an embed for the maps menu."""
        maps_embed = discord.Embed(
            title="Maps",
            description="Maps currently in Casual Ranked Bedwars rotation",
            # colour turqoise
            color=0x40e0d0
        )

        with open("maps", "r") as file:
            # csv file
            string = file.read()
            maps = string.split("\n")
            maps_embed.add_field(name="Maps", value=str("\n".join(maps)), inline=False)

        try:
            maps_embed.set_thumbnail(url=ctx.guild.icon)
        except Exception as e:
            print(e)
            print("Error getting guild image embed.")
        return maps_embed

    @commands.hybrid_command(aliases = ['map'], brief = 'Displays the map pool for the current season.')
    async def maps(self, ctx):
        """Display the map pool for the current season."""
        await ctx.reply(embed=self.create_maps_embed(ctx), mention_author=True, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Maps(bot))
