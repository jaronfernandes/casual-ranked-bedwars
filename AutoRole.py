import discord
from discord.ext import commands

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class AutoRole(commands.Cog):
    bot: commands.Bot
    SCOPES: list[str] = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    spreadsheet_id = "1TJzireUkllZVZ9kESgozudSzlJkZbCtQVGVh8xpyL5M"
    member_range: str = "A:A"
    role_range: str = "B:B"
    sheet_name = "Sheet1"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spreadsheet-id")
    async def set_spreadsheet_id(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id

    @commands.command(name="member-range")
    async def set_member_range(self, member_range):
        self.member_range = member_range

    @commands.command(name="role-range")
    async def set_role_range(self, role_range):
        self.role_range = role_range

    @commands.command(name="sheet-name")
    async def set_sheet_name(self, sheet_name):
        self.sheet_name = sheet_name

    @commands.command(name="update-roles")
    async def auto_role(self, ctx: commands.Context):
        guild = ctx.guild
        member_roles = await self._get_member_roles(guild, ctx)
        for member in member_roles:
            await member.add_roles(member_roles[member])

    async def _get_member_roles(self, guild: discord.Guild, ctx: commands.Context) -> dict[discord.Member, discord.Role]:
        member_names = self._read_spreadsheet(self.member_range)[1:]
        role_names = self._read_spreadsheet(self.role_range)[1:]

        members = list(guild.members)
        roles = list(guild.roles)

        member_roles = {}
        for i in range(len(member_names)):
            member = self.find_member(member_names[i][0], members)
            role = self.find_role(role_names[i][0], roles)

            if role and member:
                member_roles[member] = role
            elif not role:
                await ctx.send(f"Couldn't find the '{role_names[i][0]}' role.")
            else:
                await ctx.send(f"Couldn't find the member, {member_names[i][0]}.")

        return member_roles

    def _read_spreadsheet(self, spreadsheet_range: str) -> list[list[str]]:
        # Get credentials.
        credentials = self._read_credentials()

        # Call API.
        try:
            service = build("sheets", "v4", credentials=credentials)
            spreadsheet = service.spreadsheets()
            result = (
                spreadsheet.values()
                .get(spreadsheetId=self.spreadsheet_id, range=spreadsheet_range)
                .execute()
            )

            values = result.get("values", [])

            if not values:
                print("No data found.")
            else:
                return values

        except HttpError as e:
            print("Something went wrong: " + e.error_details)

    def _read_credentials(self) -> Credentials:
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run.
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

    def _get_member_range(self) -> str:
        return f"{self.sheet_name}!{self.role_range}"

    def _get_role_range(self) -> str:
        return f"{self.sheet_name}!{self.role_range}"

    """
    This method is used to get a corresponding discord.Role object.
    @return: discord.Role object if the role exists, else None.
    """
    def find_role(self, role_name: str, roles: list[discord.Role]) -> discord.Role | None:
        found_role = None

        for role in roles:
            if role.name == role_name:
                found_role = role

        return found_role

    """
    This method is used to get a corresponding discord.Member object.
    @return: discord.Member object if the member exists, else None.
    """

    def find_member(self, member_id: str, members: list[discord.Member]) -> discord.Member:
        found_member = None

        for member in members:
            if member.name == member_id:
                found_member = member

        return found_member
