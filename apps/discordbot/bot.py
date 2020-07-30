import os
import logging
import time
import threading
import asyncio


from decouple import config
import discord

TOKEN = config("DISCORD_TOKEN", default="")

logger = logging.getLogger(__name__)


class CSUAClient(discord.Client):
    async def on_ready(self):
        print(f"{self.user} has connected to Discord")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith("!register"):
            await message.channel.send("Sup")


class CSUABot:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start, daemon=True)
        self.thread.start()

    def _start(self):
        asyncio.set_event_loop(self.loop)
        self.client = CSUAClient()
        try:
            self.loop.run_until_complete(self.client.start(TOKEN))
        finally:
            self.loop.run_until_complete(self.client.logout())
            self.loop.close()

    def promote_user(self, tag):
        # TODO
        pass


if TOKEN:
    csua_bot = CSUABot()
