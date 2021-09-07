import discord
from decouple import config
import re

DISCORD_TOKEN = config('TOKEN')

patterns = ['er', 'eR', 'Er', 'ER']

client = discord.Client()

@client.event
async def on_ready():
    print('Bot is now online and ready to roll.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    for pattern in patterns:
        if re.search(pattern, message.content):
            response = re.findall(rf'\b\w+{re.escape(pattern)}\b', message.content, re.MULTILINE)
            new_response = response[0].lower().capitalize()
            await message.channel.send(new_response + "? I hardly know 'er.")

client.run(DISCORD_TOKEN)
