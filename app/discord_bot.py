import discord
import asyncio
from discord.ext import commands
from flask_sqlalchemy import SQLAlchemy
from app.secret.discord_id import discord_bot_token
from app.models import Channel, Webhook, Guild

class discord_bot(discord.Client):
    def __init__(self, parent, db, loop=None):
        if loop != None:
            super().__init__(loop=loop)
        else:
            super().__init__()
        self.parent = parent
        self.db = db
    
    # Gets a list of channels from the guild
    # Adds channel to table if not in table
    async def get_channels(self, guildId):
        channels = self.get_guild(guildId).channels
        for channel in channels:
            if type(channel) == discord.TextChannel:
                print(channel.id)
                self.addChannelToTable(channel)
        return channels

    # Gets a list of discord webhook objects linked to specified channelId
    async def get_webhooks(self, channelId):
        channel = self.get_channel(channelId)
        if type(channel) == discord.TextChannel:
            return channel.webhooks()
        return []
    
    # Creates a discord webhook and links it to the input channel id
    async def create_webhook(self, channelId):
        channel = self.get_channel(channelId)
        if type(channel) == discord.TextChannel:
            webhook = channel.create_webhook(name='Twitch Notifications')
            return self.addWebhookToTable(webhook, channelId)
        return False

    # Adds channel to table with link to parent guild
    def addChannelToTable(self, channel):
        try:
            c = Channel(channelId=channel.id, channelName=channel.name, guildId=channel.guild().id)
            self.db.session.add(c)
            self.db.session.commit()
            return True
        except Exception as e:
            print(e)
        return False
    
    # Adds webhook to table with link to parent channel
    def addWebhookToTable(self, webhook, channelId):
        try:
            w = Webhook(webhookId=webhook.id, channelId=channelId)
            self.db.session.add(w)
            self.db.session.commit()
            return True
        except Exception as e:
            print(e)
        return False

    # Adds guild to table
    def addGuildToTable(self, guildId, guildName):
        try:
            g = Guild(guildId=guildId, guildName=guildName)
            self.db.session.add(g)
            self.db.session.commit()
            return True
        except Exception as e:
            print(e)
        return False
