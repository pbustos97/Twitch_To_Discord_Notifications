import threading
import asyncio
import time
from app.discord_bot import discord_bot
from app.secret.discord_id import discord_bot_token

class Discord_Async(threading.Thread):
    def __init__(self, db):
        threading.Thread.__init__(self)
        self.discordBot = None
        self.discordLoop = asyncio.new_event_loop()
        self.db = db
        self.start()

    async def starter(self):
        self.discordBot = discord_bot(self, db=self.db)
        await self.discordBot.start(str(discord_bot_token))

    def run(self):
        self.name = "Discord.py"
        self.discordLoop.create_task(self.starter())
        self.discordLoop.run_forever()