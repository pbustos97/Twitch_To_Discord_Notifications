import discord
import asyncio
from discord.ext import commands
from flask_sqlalchemy import SQLAlchemy
from app.secret.discord_id import discord_bot_token
from app.models import Channel, Webhook, Guild, User

class discord_bot(discord.Client):
    def __init__(self, parent, db):
        super().__init__()
        self.parent = parent
        self.db = db
    
    # Gets a list of channels from the guild
    # Adds channel to table if not in table
    async def get_channels(self, guildId):
        channels = self.get_guild(guildId).channels
        for channel in channels:
            if type(channel) == discord.TextChannel:
                #print(channel.id)
                self.addChannelToTable(channel)
        return channels

    # Gets a list of discord webhook objects linked to specified channelId
    async def get_webhooks(self, channelId):
        channel = self.get_channel(channelId)
        webhooks = []
        if type(channel) == discord.TextChannel:
            webhooks = await channel.webhooks()
            for webhook in webhooks:
                self.addWebhookToTable(webhook, channelId)
        return webhooks
    
    # Creates a discord webhook and links it to the input channel id
    async def create_webhook(self, channelId):
        channel = self.get_channel(channelId)
        if type(channel) == discord.TextChannel:
            webhook = channel.create_webhook(name='Twitch Notifications')
            return self.addWebhookToTable(webhook, channelId)
        return False

    # Adds channel to table with link to parent guild
    def addChannelToTable(self, channel):
        c = Channel.query.filter_by(channelId=channel.id).first()
        try:
            if c != None:
                c.channelName = channel.name
                self.db.session.commit()
                return True
            else:
                c = Channel(channelId=channel.id, channelName=channel.name, guildId=channel.guild.id)
                self.db.session.add(c)
                self.db.session.commit()
                return True
        except Exception as e:
            print(e)
        return False
    
    # Adds webhook to table with link to parent channel
    def addWebhookToTable(self, webhook, channelId):
        if Webhook.query.filter_by(webhookId=webhook.id).first() != None:
            return True
        try:
            w = Webhook(webhookId=webhook.id, channelId=channelId, webhookURL=webhook.url)
            self.db.session.add(w)
            self.db.session.commit()
            return True
        except Exception as e:
            print(e)
        return False

    # Adds guild to table
    def addGuildToTable(self, guildId, guildName):
        g = Guild.query.filter_by(guildId=guildId).first()
        try:
            if g != None:
                g.guildName = guildName
                self.db.session.commit()
                return True
            else:
                g = Guild(guildId=guildId, guildName=guildName)
                self.db.session.add(g)
                self.db.session.commit()
                return True
        except Exception as e:
            print(e)
        return False

    # Adds user to table
    def addUserToTable(self, user):
        u = User.query.filter_by(discordId=user['discordId']).first()
        try:
            if u != None:
                u.username = user['username']
                u.discriminator = user['discriminator']
                u.email = user['email']
                self.db.session.commit()
                return True
            else:
                u = User(discordId=user['discordId'], username=user['username'], discriminator=user['discriminator'], email=user['email'], avatarURL=user['avatarURL'])
                self.db.session.add(u)
                self.db.session.commit()
                return True
        except Exception as e:
            print(e)
        return False
    
    # Checks if bot is inside of the requested guild
    def isMember(self, guildId):
        #print(self.guilds)
        #print(self.get_guild(guildId))
        if self.get_guild(guildId) in self.guilds:
            return True
        return False