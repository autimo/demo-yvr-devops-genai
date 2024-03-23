import os

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID")

# The guild ID is optional; if you omit it, the command is global and can take up to an hour to propagate
GUILD_ID = os.getenv("DISCORD_GUILD_ID")

# The URL to register a global command looks like this:
# url = f"https://discord.com/api/v9/applications/{APPLICATION_ID}/commands"

# For guild-specific commands, which update instantly, use this URL:
url = f"https://discord.com/api/v9/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands"

# Define the commands you want to register
commands = [
    {"name": "hello", "description": "Responds with Hello, YVR DevOps!", "type": 1},
    {"name": "hifive", "description": "Responds with a high five emoji!", "type": 1},
]

# Make a POST request to the Discord API to register each command
headers = {"Authorization": f"Bot {BOT_TOKEN}"}

# Register each command
for command in commands:
    response = requests.post(url, headers=headers, json=command)
    print(f"Response to registering {command['name']}:", response.json())
