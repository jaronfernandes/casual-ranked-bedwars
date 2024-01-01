import discord
from discord.ext import commands


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_rules_embed(self, ctx):
        """Return an embed for the rules."""
        rules_embed = discord.Embed(
            title="Casual Ranked Bedwars Rules",
            description="Basic Rules for Casual Ranked Bedwars games.",
            # colour yellow
            color=0xffff00
        )
        
        # { name: "First Rusher:", value: "Gets 28-36 iron to buy blocks and bridges to mid and 2 stacks (sometimes a mix of 1, 2, and 3 stack in some cases", inline: true},
        # { name: "Second Rusher:", value: "Gets a base of 12 gold to buy iron armour, and a quantity of iron to get blocks/tools/swords", inline: true},
        # { name: "Third Rusher:", value: "Drops 15-25 iron to the defender. May also get iron armour, blocks/tools/swords, and other items (fireballs)", inline: true},
        # { name: "Fourth Rusher:", value: "Gets 64 + 8 iron (or 4 gold and 48 iron) to buy an endstone/wood butterfly defense, and places it down. They then follow the others to mid.", inline: true},
        
        rules_embed.add_field(name="First Rusher:", value="Gets 28-36 iron to buy blocks and bridges to mid and 2 stacks (sometimes a mix of 1, 2, and 3 stack in some cases", inline=False)
        rules_embed.add_field(name="Second Rusher:", value="Gets a base of 12 gold to buy iron armour, and a quantity of iron to get blocks/tools/swords", inline=False)
        rules_embed.add_field(name="Third Rusher:", value="Drops 15-25 iron to the defender. May also get iron armour, blocks/tools/swords, and other items (fireballs)", inline=False)
        rules_embed.add_field(name="Fourth Rusher:", value="Gets 64 + 8 iron (or 4 gold and 48 iron) to buy an endstone/wood butterfly defense, and places it down. They then follow the others to mid.", inline=False)

        try:
            rules_embed.set_thumbnail(url=ctx.guild.icon)
        except Exception as e:
            print(e)
            print("Error getting guild image embed.")
        return rules_embed

    @commands.hybrid_command(aliases = ['r'], brief = 'View the rules for Casual Ranked Bedwars')
    async def rules(self, ctx):
        """Display the map pool for the current season."""
        await ctx.send(embed=self.create_rules_embed(ctx))

async def setup(bot):
    await bot.add_cog(Rules(bot))