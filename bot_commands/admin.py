import discord, os
from discord import app_commands
from discord.ext import commands
from datetime import date
from data_access import reset_season, SetupELORoles, get_elo_distribution

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # For resetting season
    class SeasonUpdateView(discord.ui.View):
        has_interacted = False
        bot: commands.Bot

        def __init__(self, ctx):
            super().__init__(timeout=60)
            self.ctx = ctx
            self.bot = ctx.bot

        @discord.ui.button(label="Reset Season", style=discord.ButtonStyle.green)
        async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("You do not have permission to do this!", ephemeral=True)
                return
            elif self.has_interacted:
                await interaction.response.send_message("You have already responded to this message!", ephemeral=True)
                return
            else:
                self.has_interacted = True

                await interaction.response.defer()
                
                successful_reset, season = await reset_season(interaction.user.guild)
                
                if successful_reset:
                    await interaction.followup.send(content="Successfully updated to season " + str(season) + "!", ephemeral=True)
                else:
                    await interaction.followup.send(content="There was an error setting the new season!\nPlease check the console for more information.", ephemeral=True)

        @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("You do not have permission to do this!", ephemeral=True)
                return
            elif self.has_interacted:
                await interaction.response.send_message("You have already responded to this message!", ephemeral=True)
                return
            else:
                self.has_interacted = True
                await interaction.response.send_message("Did not reset the season!", ephemeral=True)

    @commands.has_permissions(administrator=True)
    @commands.hybrid_command(aliases = ['a','ac', 'admin_commands', 'admin-commands', 'admin-cmds', 'admin_cmds', 'acmds', 'a-cmds'], brief = 'Executes an admin command (admins only)', description = 'Execute an admin command (admin only), or view the list of admin commands (default).')
    @app_commands.describe(option='Type of admin command to execute')
    async def admin(self, ctx: commands.Context, option=None):
        """Display the map pool for the current season."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply(content="You do not have the permission to do this!", mention_author=True, ephemeral=True)
        elif option != None and option.lower() == 'reset-season':
            await ctx.reply(content="Are you sure you want to end this season and start a new one?", view=self.SeasonUpdateView(ctx), mention_author=True, ephemeral=True)
        elif option != None and option.lower() == 'setup-roles':
            elo_dict = get_elo_distribution(ctx.guild.id)

            for elo_key in elo_dict:  # Check if the roles exist
                if elo_dict[elo_key][4] == "N/A" or all(elo_dict[elo_key][4] != str(role.id) for role in ctx.guild.roles):
                    new_view = SetupELORoles()
                    await ctx.reply(content="It seems the roles for the ELO distribution have not been set up yet. Would you like to set them up now?", mention_author=True, view=new_view, ephemeral=True)
                    return
            
            await ctx.reply(content="The roles for the ELO distribution have already been set up!", mention_author=True, ephemeral=True)
        
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
            help_embed.add_field(name="setup-roles", value="Setup prestige roles, if they are not already set up", inline=False)
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
