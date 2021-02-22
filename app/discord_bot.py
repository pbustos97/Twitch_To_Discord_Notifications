import discord
import asyncio
from discord.ext import commands
from secret.discord_id import discord_bot_token

class discord_bot(discord.Client):
    def __init__(self, parent, loop):
        super().__init__(loop=loop)
        self.parent = parent
    
    # Gets a list of channels from the guild
    # Adds channel to table if not in table
    async def get_channels(self, guildId):
        channels = self.get_guild(guildId).fetch_channels()
        #for channel in channels:
        #    addChannelToTable(channel)
        #return channels

    # Gets a list of webhooks per channel
    # Webhooks should already be in database
    async def get_webhooks(self, channelId):
        return self.get_channel(channelId)
    
    # Creates a webhook and links it to the input channel id
    async def create_webhook(self, channelId):
        return