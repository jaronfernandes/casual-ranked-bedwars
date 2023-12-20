import discord, json
from discord.ext import commands
from data_access import setup_guild_in_json_file


class Season(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_season_embed(self, current_guild: discord.Guild) -> discord.Embed:
        """Return an embed for the current season.
        
        Preconditions:
        - current_guild_id is the ID of the current guild.
        """
        current_guild_id = current_guild.id

        with open("data", "r") as file:
            string = file.read()
            data = json.loads(string)

            if str(current_guild_id) not in data["SERVERS"]:
                setup_guild_in_json_file(current_guild_id)
                print(f"Created new server {current_guild_id} in data file.")
                with open("data", "r") as file:
                    string = file.read()
                    data = json.loads(string)

            current_season = data["SERVERS"][str(current_guild_id)]["current_season"]
            season = current_season["season"]
            start_date = current_season["start_date"]
            end_date = current_season["end_date"]
            banned_items = current_season["banned_items"]

            embed = discord.Embed(
                title= current_guild.name + " | Season " + str(season),
                description="Season " + str(season) + " started on " + start_date + (" and ended on " + end_date + "." if end_date != "N/A" else "."),
                # aqua colour
                color= 0x00ffff
            )

            plrs = []
            # get top players based on ELO below
            for player in data["SERVERS"][str(current_guild_id)]["user_data"]:
                plrs.append({
                    "ID": player,
                    "ELO": data["SERVERS"][str(current_guild_id)]["user_data"][player]["ELO"]
                    })
            top_players = sorted(plrs, key=lambda k: k["ELO"], reverse=True)[:10]
            top_players_str = ""

            count = 1

            for player in top_players:
                top_players_str += f"{(str(count) + '. <@' + str(player['ID']) + '>') : <30}" + "\t ELO: " + str(player["ELO"]) + "\n"
                count += 1

            embed.add_field(name="Top Players", value=top_players_str, inline=False)

            embed.add_field(name="Banned Items", value=str("\n".join(banned_items)), inline=True)

            season_stats_str = \
                "Total Matches: " + str(current_season["total_games_played"]) + "\n"

            embed.add_field(name="Season Statistics", value=season_stats_str)

            try:
                embed.set_thumbnail(url=current_guild.icon)
            except Exception as e:
                print(e)
                print("Error getting guild image embed.")

            return embed

    @commands.hybrid_command(aliases = ['ssn', 'szn'], brief = 'season #', description = "View the current season")
    async def season(self, ctx):
        """Display the map pool for the current season."""
        await ctx.send(embed=self.create_season_embed(ctx.guild))

async def setup(bot):
    await bot.add_cog(Season(bot))
