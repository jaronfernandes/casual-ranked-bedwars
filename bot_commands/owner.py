import discord, os
from discord import app_commands
from discord.ext import commands
from datetime import date
from data_access import backup_data, clear_data

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # For Backups
    class BackupView(discord.ui.View):
        has_interacted = False
        bot: commands.Bot

        def __init__(self, ctx):
            super().__init__(timeout=60)
            self.ctx = ctx
            self.bot = ctx.bot

        @discord.ui.button(label="Backup Data", style=discord.ButtonStyle.green)
        async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.id == self.bot.owner_id:
                await interaction.response.send_message("You do not have permission to do this!", ephemeral=True)
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
            if not interaction.user.id == self.bot.owner_id:
                await interaction.response.send_message("You do not have permission to do this!", ephemeral=True)
                return
            elif self.has_interacted:
                await interaction.response.send_message("You have already responded to this message!", ephemeral=True)
                return
            else:
                self.has_interacted = True
                await interaction.response.send_message("Did not backup data!", ephemeral=True)

    # For clearing data
    class ClearDataView(discord.ui.View):
        has_interacted = False
        bot: commands.Bot

        def __init__(self, ctx):
            super().__init__(timeout=60)
            self.ctx = ctx
            self.bot = ctx.bot

        @discord.ui.button(label="Clear Data", style=discord.ButtonStyle.green)
        async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.id == self.bot.owner_id:
                await interaction.response.send_message("You do not have permission to do this!", ephemeral=True)
                return
            elif self.has_interacted:
                await interaction.response.send_message("You have already responded to this message!", ephemeral=True)
                return
            else:
                self.has_interacted = True
                
                successful_backup = clear_data()
                
                if successful_backup:
                    await interaction.response.send_message("Successfully cleared all data!", ephemeral=True)
                else:
                    await interaction.response.send_message("There was an error clearing data!\nPlease check the console for more information.", ephemeral=True)

        @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.id == self.bot.owner_id:
                await interaction.response.send_message("You do not have permission to do this!", ephemeral=True)
                return
            elif self.has_interacted:
                await interaction.response.send_message("You have already responded to this message!", ephemeral=True)
                return
            else:
                self.has_interacted = True
                await interaction.response.send_message("Did not clear data!", ephemeral=True)

    @commands.is_owner()
    @commands.hybrid_command(aliases = ['o', 'oc', 'ocmds'], brief = 'Executes an owner-only command (bot owner only)', description = 'Executes an owner-only command (bot owner only).')
    @app_commands.describe(option='Type of owner-only command to execute')
    async def owner(self, ctx: commands.Context, option=None):
        """Display the map pool for the current season."""
        if option != None and option.lower() == 'backup':
            await ctx.reply(content="Are you sure you want to backup the current bot data?", view=self.BackupView(ctx), mention_author=True, ephemeral=True)
        elif option != None and option.lower() == 'clear-data':
            await ctx.reply(content="Are you sure you want to clear ALL bot data? **WARNING: THIS IS IRREVERSIBLE!**", view=self.ClearDataView(ctx), mention_author=True, ephemeral=True)
        elif option != None and not option.lower() == 'help':
            await ctx.reply(content="Invalid admin command! Please use /admin or /admin help to view the list of admin commands, or use /admin [command] to execute an admin command.", mention_author=True, ephemeral=True)
        else:  # No option specified
            help_embed = discord.Embed(
                title="Casual Ranked Bedwars Owner Commands",
                description="Use Slash (/) Interactions or the prefix ! to execute commands.",
                # fairy-tale like colour
                color=0xff69b4
            )   

            help_embed.add_field(name="help", value="View all the owner-only commands", inline=False)
            help_embed.add_field(name="backup", value="Backup the current bot data", inline=False)
            help_embed.add_field(name="clear-data", value="Reset all the current data (IRREVERSIBLE)", inline=False)

            try:
                help_embed.set_thumbnail(url=ctx.guild.icon)
            except Exception as e:
                print(e)
                print("Error getting guild image embed.")

            await ctx.reply(embed=help_embed, mention_author=True, ephemeral=True)
            # ctx.interaction.response.send_message(help_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Owner(bot))
