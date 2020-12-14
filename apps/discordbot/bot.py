import os
import logging
import time
import threading
import asyncio
import unicodedata

from decouple import config
import discord
from discord.utils import get, find
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import reverse

from utils import send_verify_mail

TOKEN = config("DISCORD_TOKEN", default="")

TIMEOUT_SECS = 10

CSUA_GUILD_ID = 368282532757897217      #Old CSUA Discord
HOSER_ROLE_ID = 368285558167830529
NEW_CSUA_GUILD_ID = 784902200102354985  #New CSUA Discord
HOSER_2_ROLE_ID = 785418569412116513

TEST_GUILD_ID = 737934159388868624
TEST_CHANNEL_ID = 737934159833595966

logger = logging.getLogger(__name__)


class CSUAClient(discord.Client):
    async def on_ready(self):
        print(f"{self.user} has connected to Discord")
        self.csua_guild = get(self.guilds, id=NEW_CSUA_GUILD_ID)
        self.test_guild = get(self.guilds, id=TEST_GUILD_ID)
        self.test_channel = get(self.test_guild.channels, id=TEST_CHANNEL_ID)
        self.hoser_role = get(self.csua_guild.roles, id=HOSER_2_ROLE_ID)

    async def verify_member_email(self, user): 
        channel = user.dm_channel
        def check_msg(msg, user):
            return msg.channel == channel
        got_email = False
        while not got_email:
            msg = await self.wait_for('message', check=check_msg)
            try:
                validate_email(msg)
                got_email= True
                await channel.send(f"Sending a an email to verify {user.name} to {msg}")
                send_verify_mail(msg, user.name)
            except ValidationError as e:
                await channel.send(f"{msg} is not a valid email. Please try again. Details: ", e)
    
    async def on_message(self, message):
        if message.author == self.user:
            return

        #Reading rules and verification


        msg = message.content.lower()
        if "hkn" in msg.lower() and "ieee" in msg.lower():
            await message.channel.send("Do I need to retrieve the stick?")
        if "is typing..." in msg:
            await message.channel.send("unoriginal")
        elif "based" in msg:
            for c in "based":
                emoji = unicodedata.lookup(f"REGIONAL INDICATOR SYMBOL LETTER {c}")
                await message.add_reaction(emoji)
            await message.add_reaction("😎")

    async def on_member_join(self, member):
        await member.send(
            "Welcome to the CSUA discord server! First, read the rules in #landing-zone. Thumbs up this message if you agree")
        channel = member.dm_channel
        def check_thumb(react, user):
            return user == member and str(react.emoji) == '👍' # thumbs
        await self.wait_for('reaction_add', check=check_thumb)
        await member.send(
            "Verify your berkeley.edu email to gain access. First, pleast type your email. Please contact a moderator if you have any issues."
        )


        url = "https://www.csua.berkeley.edu" + reverse("discord_register")
        await member.send(url)
        await self.test_channel.send(f"{member} was sent registration invite message")

    async def on_member_remove(self, member):
        pass


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
