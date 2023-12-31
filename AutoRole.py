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
    SPREADSHEET_ID = "1TJzireUkllZVZ9kESgozudSzlJkZbCtQVGVh8xpyL5M"
    column_start = 0
    column_end = 0
    row_start = 0
    row_end = 0

    def __init__(self, bot, spreadsheet_link):
        self.bot = bot
        self.spreadsheet_link = spreadsheet_link

    @commands.command()
    async def assign_roles(self, ctx):
        member_roles = self._get_member_roles()
        for member in member_roles:
            await member.add_roles(member_roles[member])
            print(f"Added role to {member.name}")

    def _get_member_roles(self) -> dict[discord.Member, discord.Role]:
        spreadsheet_data = self._read_spreadsheet()
        member_roles = {}
        for member_name in member_role_names:
            member = self.find_member(member_name);
            role = self.find_role(member_role_names[member_name])
            member_roles[member] = role

        return member_roles

    def _read_spreadsheet(self) -> list[list[str]]:
        # Get credentials.
        credentials = self._read_credentials()

        # Call API.

        try:
            service = build("sheets", "v4", credentials=credentials)
            spreadsheet = service.spreadsheets()
            spreadsheet_range = self._get_spreadsheet_range()
            result = (
                spreadsheet.values()
                .get(spreadsheetId=self.SPREADSHEET_ID, range=spreadsheet_range)
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

    def _get_spreadsheet_range(self) -> str:
        row_start = self.row_start
        row_end = self.row_end

        if self.row_start == -1:
            row_start = ""
        if self.row_end == -1:
            row_end = ""

        return f"Class Data!{self.column_start}{row_start}:{self.column_end}{row_end}"

    def find_role(self, role_name: str) -> discord.Role:
        return

    def find_member(self, id: str) -> discord.Member:
        return
