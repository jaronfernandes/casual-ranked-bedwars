# **casual-ranked-bedwars bot**
```python
developer = "Jaron Fernandes"
contributors = []
github = "https://github.com/jaronfernandes"
```

# Features 
- **Slash and Prefix Commands**
- **File Data Storage** (stored on your computer so you can ~~modify~~ view user data)
- **User + Season Statistics and Leaderboards** (settling the GOAT debate of casual ranked bedwars)
- **Assisted Scoring** (saves you from visiting the elo distribution file)
- **Independent Server Data** (let the bot thrive in multiple guilds, since why not?)
- **Role and Channel Setup Commands** (to make your life easier!)


# Description

A fully functional Casual Ranked Bedwars Discord bot I made for my friends in a small Discord server. Decided to upload it to Github two and a half years later because why not?

Initially created in January 2021 using discord.js, it migrated to discord.py in December-January 2023 after severe deprecation from Discord updates.

This bot is meant for small servers as it uses a volatile file saving system that is stored on your computer.


# Setup

- Change .env.example to .env, and assign your Discord bot token to TOKEN.
- Run `python main.py` in the terminal (or `python3 main.py`)
- Feel free to edit *some* of the contents of files such as maps or elo-distribution.


# Requirements:
- Python (3.6+, preferably 3.10+)
- Dependencies (see `requirements.txt`):
    - discord.py (2.3.2) 
    - dotenv (1.0.0)

- **Note for MacOS users:**
If you are a macOS user, navigate to the Applications/Python 3.11/ (or a different Python version, usually 3.6+) folder and double click on "Install Certificates.command".


# List of Commands
| Command | Options | Description |
| ------------- |:-------------:| -----:|
| **play** |  | Begin a new game |
| **help** | | View the help menu |
| **stats** | [`username`] | Get your current or another user's season statistics |
| **season** | [`season #`] | View the statistics for the current or a past season |
| **rules** | | View the rules and instructions for Casual Ranked Bedwars |
| **info** | | View the current elo distribution for Casual Ranked Bedwars |
| **maps** | | View the maps currently in rotation |
| **leaderboard** | [`ELO, Wins, W/L Ratio, Winstreak`] [`page #`] | View the leaderboard for several statistics |
| **admin** | [`cmd`] | All admin commands (default displays a list of admin commands) |
| **owner** | [`cmd`] | All *bot* owner commands (default displays a list of bot owner commands) |
