# **casual-ranked-bedwars bot**

```python
developer = "Jaron Fernandes"
github = "https://github.com/jaronfernandes"
```

# **IMPORTANT NOTE:**

This bot is currently being revamped! It will come with many new features on top of the existing ones:

- Slash Commands (these didn't exist when I created the bot)
- Enhanced Data Storage (so you'll save braincells by not viewing my code)
- Custom Match Settings for Individual Servers (different tastes, different games!)
- User Statistics (settling the GOAT debate of casual ranked bedwars)
- Role and Channel Setup Commands (to make your life easier!)

# Description

A (formerly) fully functional Casual Ranked Bedwars Discord bot I made for my friends in a small Discord server. Decided to upload it to Github two and a half years later because why not?

Created (and finished) in January 2021, it has been subjected to severe deprecation due to Discord updates as it was originally built for some Discord.js version 12. My inactivity on casual ranked bedwars subsequently led to the project not being supported anymore. Due to these unforeseen updates, expect some features to not work.

This bot is meant for small servers. It takes advantage of Discord's messaging system by using a message the bot sends, and manipulates it to hold its own little database of player statistics. You will have to modify this system to accomodate more players or use an external database.

Feel free to edit the array of maps and the other settings to whatever is up-to-date or to your liking.

# Requirements:

- discord, dotenv, python (preferably 3.6+)
  FOR PYTHON:
- If you are a macOS user, navigate to the Applications/Python 3.11/ (or a different Python version, usually 3.6+) folder and double click on "Install Certificates.command".

# Set-up

## Roling Functionality

- Set an environment variable named TOKEN with your bot's token.
- Ensure that your bot's role is higher in the role hierarchy than the roles that are being assigned.
- Future improvements - conversion to slash command, on-Discord customisability for spreadsheet range, etc., and manual roling.
