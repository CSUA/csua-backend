import os
import logging
import time
import threading
import asyncio
import socket
import unicodedata

from decouple import config
import discord
from discord.utils import get
from django.urls import reverse

TOKEN = config("DISCORD_TOKEN", default="")

TIMEOUT_SECS = 10

CSUA_PHILBOT_CLIENT_ID = 737930184837300274

# You may have to modify these
CSUA_GUILD_ID = 368282532757897217
HOSER_ROLE_ID = 368285558167830529

TEST_GUILD_ID = 737934159388868624
TEST_CHANNEL_ID = 737934159833595966

logger = logging.getLogger(__name__)


class CSUAClient(discord.Client):
    async def on_ready(self):
        print(f"{self.user} has connected to Discord")
        self.is_phillip = self.user.id == CSUA_PHILBOT_CLIENT_ID
        if self.is_phillip:
            self.csua_guild = get(self.guilds, id=CSUA_GUILD_ID)
            self.test_guild = get(self.guilds, id=TEST_GUILD_ID)
            self.test_channel = get(self.test_guild.channels, id=TEST_CHANNEL_ID)
            self.hoser_role = get(self.csua_guild.roles, id=HOSER_ROLE_ID)

    async def on_message(self, message):
        if message.author == self.user:
            return
        msg = message.content.lower()
        if msg == "piss":
            await message.channel.send("shid")
        elif msg == "poo" or msg == "poop":
            await message.channel.send("funny poopies")
        elif msg == "uh oh":
            await message.channel.send("stinky")
        elif "based" in msg:
            for c in "based":
                emoji = unicodedata.lookup(f"REGIONAL INDICATOR SYMBOL LETTER {c}")
                await message.add_reaction(emoji)
            await message.add_reaction("😎")

    async def on_member_join(self, member):
        await member.send(
            "Welcome to the CSUA discord server! Verify your berkeley.edu email to gain access. Please contact a moderator if you have any issues."
        )
        url = "https://www.csua.berkeley.edu" + reverse("discord_register")
        await member.send(url)
        if self.is_phillip:
            await self.test_channel.send(
                f"{member} was sent registration invite message"
            )


class CSUABot:
    """
    Wraps CSUAClient by abstracting thread and event loop logic.

    All the discord.Client coroutines must be called using
    `asyncio.run_coroutine_threadsafe` because the client is running inside an
    event loop in a separate thread. Event loops are one per-thread, and Django
    can't handle async code, so a separate thread is used instead.
    """

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

    def promote_user_to_hoser(self, tag):
        member = self.client.csua_guild.get_member_named(tag)
        if member:
            asyncio.run_coroutine_threadsafe(
                member.add_roles(self.client.hoser_role), self.loop
            ).result(TIMEOUT_SECS)
            return True
        return False


if TOKEN:
    csua_bot = CSUABot()
else:
    csua_bot = None
