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
    member_range: str = "A:A"
    role_range: str = "B:B"
    sheet_name = "Sheet1"

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
        members = self._read_spreadsheet(self.member_range)[1:]
        roles = self._read_spreadsheet(self.member_range)[1:]

        member_roles = {}
        for i in range(len(members)):
            member = self.find_member(members[i][0])
            role = self.find_role(roles[i][0])
            member_roles[member] = role

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
                .get(spreadsheetId=self.SPREADSHEET_ID, range=spreadsheet_range)
                .execute()
            )

            values = result.get("values", [])

            if not values:
                print("No data found.")
            else:
                print(values)
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

    def find_role(self, role_name: str) -> discord.Role:
        return

    def find_member(self, id: str) -> discord.Member:
        return
