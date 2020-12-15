import logging
import threading
import asyncio
import unicodedata

from decouple import config
import discord
from discord.utils import get
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .utils import send_verify_mail

intents = discord.Intents.all()
intents.presences = False

TOKEN = config("DISCORD_TOKEN", default="")
CSUA_GUILD_ID = config("TEST_GUILD", default=368282532757897217, cast=int)
CSUA_PHILBOT_CLIENT_ID = config("BOT_ID", default=737930184837300274, cast=int)
HOSER_ROLE_ID = config("TEST_ROLE", default=785418569412116513, cast=int)  # Verified
DEBUG_CHANNEL_ID = config("DEBUG_CHANNEL", default=787853294474100756, cast=int)

TIMEOUT_SECS = 10

logger = logging.getLogger(__name__)


class CSUAClient(discord.Client):
    async def on_ready(self):
        print(f"{self.user} has connected to Discord")
        self.is_phillip = self.user.id == CSUA_PHILBOT_CLIENT_ID
        if self.is_phillip:
            print("Phillip is in the Office")
            self.csua_guild = get(self.guilds, id=CSUA_GUILD_ID)
            self.test_channel = get(self.csua_guild.channels, id=DEBUG_CHANNEL_ID)
            self.hoser_role = get(self.csua_guild.roles, id=HOSER_ROLE_ID)

    async def verify_member_email(self, user):
        channel = user.dm_channel

        def check_msg(msg):
            return msg.channel == channel

        got_email = False
        while not got_email:
            msg = await self.wait_for("message", check=check_msg)
            try:
                validate_email(msg.content)
                if "@berkeley.edu" in msg.content:
                    got_email = True
                    await channel.send(
                        f"Sending a an email to verify {user.name} to {msg.content}"
                    )
                    send_verify_mail(msg.content, user.name)
                else:
                    await channel.send(
                        f"{msg.content} is not a berkeley email. Please fix this"
                    )
            except ValidationError as e:
                await channel.send(
                    f"{msg.content} is not a valid email. Please try again. Details: ",
                    e,
                )

    async def on_message(self, message):
        if message.author == self.user:
            return
        # Reading rules and verification
        msg = message.content.lower()
        if "hkn" in msg.lower() and "ieee" in msg.lower():
            await message.channel.send("Do I need to retrieve the stick?")
        if "is typing" in msg:
            await message.channel.send("unoriginal")
        elif "based" in msg:
            for c in "based":
                emoji = unicodedata.lookup(f"REGIONAL INDICATOR SYMBOL LETTER {c}")
                await message.add_reaction(emoji)
            await message.add_reaction("😎")

    async def on_member_join(self, member):
        msg = await member.send(
            "Welcome to the CSUA discord server! First, read the rules in #landing-zone. Thumbs up this message if you agree"
        )

        def check_thumb(react, _):
            return react.message == msg and str(react.emoji) == "👍"  # thumbs

        await self.wait_for("reaction_add", check=check_thumb)
        await member.send(
            "Verify your berkeley.edu email to gain access. First, pleast type your email. Please contact a moderator if you have any issues."
        )

        await self.verify_member_email(member)
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
        self.client = CSUAClient(intents=intents)

        try:
            self.loop.run_until_complete(self.client.start(TOKEN))
        finally:
            self.loop.run_until_complete(self.client.logout())
            self.loop.close()

    def promote_user_to_hoser(self, tag):
        member = self.client.csua_guild.get_member_named(tag)
        if member:
            assert self.client.hoser_role is not None, "Hoser Role is None"
            asyncio.run_coroutine_threadsafe(
                member.add_roles(self.client.hoser_role), self.loop
            ).result(TIMEOUT_SECS)
            return True
        return False


if TOKEN:
    csua_bot = CSUABot()
else:
    raise RuntimeError("Token missing")
