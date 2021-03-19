import threading
import asyncio
import time
from app.discord_bot import discord_bot
from app.secret.discord_id import discord_bot_token

class Discord_Async(threading.Thread):
    def __init__(self, loop, db):
        threading.Thread.__init__(self)
        self.discordBot = None
        self.discordLoop = loop
        self.db = db

    def run(self):
        asyncio.set_event_loop(self.discordLoop)
        self.discordBot = discord_bot(self, db=self.db, loop=self.discordLoop)
        self.discordBot.run(str(discord_bot_token))