import discord, os
from discord import app_commands
from discord.ext import commands
from datetime import date
from data_access import backup_data

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.hybrid_command(aliases = ['a','ac', 'admin_commands', 'admin-commands', 'admin-cmds', 'admin_cmds', 'acmds', 'a-cmds'], brief = 'Executes an admin command (admins only)', description = 'Execute an admin command (admin only), or view the list of admin commands (default).')
    @app_commands.describe(option='Type of admin command to execute')
    async def admin(self, ctx: commands.Context, option=None):
        """Display the map pool for the current season."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply(content="You do not have the permission to do this!", mention_author=True, ephemeral=True)

        elif option != None and option.lower() == 'reset-season':
            await ctx.reply(content="Are you sure you want to end this season and start a new one?", view=self.SeasonUpdateView(ctx), mention_author=True, ephemeral=True)
        elif option != None and not option.lower() == 'help':
            await ctx.reply(content="Invalid admin command! Please use /admin or /admin help to view the list of admin commands, or use /admin [command] to execute an admin command.", mention_author=True, ephemeral=True)
        else:  # No option specified
            help_embed = discord.Embed(
                title="Casual Ranked Bedwars Admin Commands",
                description="Use Slash (/) Interactions or the prefix ! to execute commands.",
                # colour dark red
                color=0x8b0000
            )   

            help_embed.add_field(name="help", value="View all the admin-only commands", inline=False)
            help_embed.add_field(name="score", value="Score a game", inline=False)
            help_embed.add_field(name="reset-season", value="Reset the season to a new one", inline=False)

            try:
                help_embed.set_thumbnail(url=ctx.guild.icon)
            except Exception as e:
                print(e)
                print("Error getting guild image embed.")

            await ctx.reply(embed=help_embed, mention_author=True, ephemeral=True)
            # ctx.interaction.response.send_message(help_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
