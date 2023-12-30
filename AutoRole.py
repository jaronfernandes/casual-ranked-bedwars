import discord
from discord.ext import commands

class AutoRole(commands.Cog):
    bot: commands.Bot
    spreadsheet_link: str

    def __init__(self, bot, spreadsheet_link):
        self.bot = bot
        self.spreadsheet_link = spreadsheet_link

    @commands.command()
    async def assign_roles(self, ctx):
        member_roles: dict[discord.Member, discord.Role] = self._get_member_roles()
        for member in member_roles:
            await member.add_roles(member_roles[member])
            print(f"Added role to {member.name}")

    def _get_member_roles(self, member_role_names: dict[str, str]) -> dict[discord.Member, discord.Role]:
        member_roles = {}
        for member_name in member_role_names:
            member = self.find_member(member_name);
            role = self.find_role(member_role_names[member_name])
            member_roles[member] = role

        return member_roles

    def read_spreadsheet(self):
        return {}

    def find_role(self, role_name: str) -> discord.Role:
        return

    def find_member(self, id: str) -> discord.Member:
        return




