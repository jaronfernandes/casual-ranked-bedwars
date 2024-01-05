import discord
from discord import app_commands
from discord.ext import commands
from datetime import date
from data_access import backup_data

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # For Backups
    class BackupView(discord.ui.View):
        has_interacted = False

        def __init__(self, ctx):
            super().__init__(timeout=60)
            self.ctx = ctx

        @discord.ui.button(label="Backup Data", style=discord.ButtonStyle.green)
        async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("You do not have permission to do this!", ephemeral=True)
                return
            elif interaction.user.id != self.ctx.author.id:
                await interaction.response.send_message("You are not the person who invoked this command!", ephemeral=True)
                return
            elif self.has_interacted:
                await interaction.response.send_message("You have already responded to this message!", ephemeral=True)
                return
            else:
                self.has_interacted = True
                
                successful_backup = backup_data()
                
                if successful_backup:
                    await interaction.response.send_message("Successfully saved the latest data to file backup_data_" + str(date.today()) + ".json!", ephemeral=True)
                else:
                    await interaction.response.send_message("There was an error backing up data!\nPlease check the console for more information.", ephemeral=True)

        @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("You do not have permission to do this!", ephemeral=True)
                return
            elif interaction.user.id != self.ctx.author.id:
                await interaction.response.send_message("You are not the person who invoked this command!", ephemeral=True)
                return
            elif self.has_interacted:
                await interaction.response.send_message("You have already responded to this message!", ephemeral=True)
                return
            else:
                self.has_interacted = True
                await interaction.response.send_message("Did not backup data!", ephemeral=True)

    @commands.has_permissions(administrator=True)
    @commands.hybrid_command(aliases = ['a','ac', 'admin_commands', 'admin-commands', 'admin-cmds', 'admin_cmds', 'acmds', 'a-cmds'], brief = 'Executes an admin command (admins only)', description = 'Execute an admin command (admin only), or view the list of admin commands (default).')
    @app_commands.describe(option='Type of admin command to execute')
    async def admin(self, ctx: commands.Context, option=None):
        """Display the map pool for the current season."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have permission to do this!")
            return
        elif option == 'Backup':
            await ctx.send("Are you sure you want to backup the current bot data?", view=self.BackupView(ctx))
        elif option == 'SeasonUpdate':
            await ctx.send("Are you sure you want to end this season and start a new one?", view=self.SeasonUpdateVisssew(ctx))

async def setup(bot):
    await bot.add_cog(Admin(bot))
