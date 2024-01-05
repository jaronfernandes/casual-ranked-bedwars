import discord
from discord.ext import commands
from discord.ui import Button, button
from typing import Optional, Union
import asyncio
from data_access import get_elo_distribution, get_admin_role, setup_elo_roles


class SetupELORoles(discord.ui.View):
    has_interacted_with: bool

    def __init__(self) -> None:
        super().__init__()
        self.has_interacted_with = False

    @button(label='Setup Roles', style=discord.ButtonStyle.green, custom_id="setup_roles_button")
    async def randomize_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True
        self.clear_items()
        await interaction.response.defer()
        # await asyncio.sleep()
        if await setup_elo_roles(interaction.guild):
            await interaction.followup.send(content='Roles have been set up!', ephemeral=True)
            # await interaction.response.edit_message(content='Roles have been set up!', view=self)
            return
        else:
            await interaction.followup.send(content='Roles failed to set up. Please fix your roles or try again. \n\
                Otherwise, submit an issue to https://github.com/jaronfernandes/casual-ranked-bedwars', ephemeral=True)
            return
        

    @button(label='Cancel', style=discord.ButtonStyle.danger, custom_id="cancel_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.has_interacted_with:
            await interaction.response.send_message('This message has expired!', ephemeral=True)
            return
        
        self.has_interacted_with = True

        self.clear_items()
        await interaction.response.edit_message(content='You canceled the role setup!', view=self)


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_info_embed(self, ctx) -> Optional[Union[discord.Embed, discord.Embed]]:
        """Return an embed for the rules."""
        info_embed = discord.Embed(
            title="Casual Ranked Bedwars ELO",
            description="ELO Distribution for Casual Ranked Bedwars games.\n1st, 2nd, and 3rd are the top 3 killers in the game.",
            # colour yellow
            color=0xffff00
        )
        elo_dict = get_elo_distribution(ctx.guild.id)
        
        for elo_key in elo_dict:
            # elo is a list of tuples
            # Generate code for a value string: Win: 30, Loss: 15, Top killer: , Second killer: , Third Killer: 
            value_string = f'<@&{elo_dict[elo_key][4]}> | Win: {elo_dict[elo_key][2]} | Loss: {elo_dict[elo_key][3]} | 1st: {elo_dict[elo_key][5]} | 2nd: {elo_dict[elo_key][6]} | 3rd: {elo_dict[elo_key][7]}'
            # NEED TO WORK ON THE BELOW ONCE SETUP_ELO_ROLES IS DONE.
            if elo_dict[elo_key][4] == "N/A" or all(elo_dict[elo_key][4] != str(role.id) for role in ctx.guild.roles):
                admin_role = get_admin_role(ctx.guild.id)
                if ctx.author.guild_permissions.administrator or any(admin_role == role.id for role in ctx.author.roles):
                    return "Setting up ELO roles"
                else:
                    return "Not set up yet"
            else:
                info_embed.add_field(name=f'{elo_dict[elo_key][0]}', value=value_string, inline=False)

        try:
            info_embed.set_thumbnail(url=ctx.guild.icon)
        except Exception as e:
            print(e)
            print("Error getting guild image embed.")
        return info_embed

    @commands.hybrid_command(aliases = ['i', 'i elo', 'information elo', 'info elo'], brief = 'i elo', description = 'View information regarding Casual Ranked Bedwars ELO')
    async def info(self, ctx):
        """Display the elo distribution."""
        info_embed_object = self.create_info_embed(ctx)
        if info_embed_object == "Setting up ELO roles":
            new_view = SetupELORoles()
            await ctx.reply(content="It seems the roles for the ELO distribution have not been set up yet. Would you like to set them up now?", ephemeral=True, mention_author=True, view=new_view)
        elif info_embed_object == "Not set up yet":
            await ctx.reply(content="It seems the roles for the ELO distribution have not been set up yet. Please contact an admin.", ephemeral=True, mention_author=True)
        else:
            await ctx.reply(embed=self.create_info_embed(ctx), ephemeral=True, mention_author=True)

async def setup(bot):
    await bot.add_cog(Info(bot))