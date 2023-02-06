import asyncio
import logging
import threading
import time
import unicodedata
from functools import partial

import discord
import schedule
from decouple import config
from discord import Forbidden, HTTPException, NotFound
from discord.embeds import Embed
from discord.utils import get
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from pyfiglet import figlet_format

from . import connect4, cowsay, xkcd
from .annoucements import AnnouncementType, get_events_in_time_delta
from .utils import send_verify_mail

intents = discord.Intents.all()
intents.presences = False

DEBUG = config("DJANGO_DEBUG", cast=bool, default=False)
TOKEN = config("DISCORD_TOKEN", default="")
CSUA_GUILD_ID = config("TEST_GUILD", default=784902200102354985, cast=int)
CSUA_PHILBOT_CLIENT_ID = config("BOT_ID", default=737930184837300274, cast=int)
HOSER_ROLE_ID = config("TEST_ROLE", default=785418569412116513, cast=int)  # Verified
DEBUG_CHANNEL_ID = config(
    "DEBUG_CHANNEL", default=788989977794707456, cast=int
)  # phil-n-carl
CSUA_CHATTER_CHANNEL_ID = 784902200102354989
CSUA_ROOT_CHANNEL_ID = 839433106868142092
ANNOUNCEMENTS_CHANNEL_ID = config(
    "ANNOUNCEMENTS_CHANNEL", default=CSUA_ROOT_CHANNEL_ID, cast=int
)
# TEST_SERVER_CHANNEL_ID = 805590450136154125  # CSUA-Test
CSUA_PB_ROLE_ID = 784907966532288542

TIMEOUT_SECS = 10

logger = logging.getLogger(__name__)


class CSUAClient(discord.Client):
    async def on_ready(self):
        print(f"{self.user} has connected to Discord")
        self.is_phillip = self.user.id == CSUA_PHILBOT_CLIENT_ID
        # csua_bot.announcements_thread = threading.Thread(
        #     target=csua_bot.event_announcement, daemon=True
        # )
        # csua_bot.announcements_thread.start()
        if self.is_phillip:
            self.csua_guild = get(self.guilds, id=CSUA_GUILD_ID)
            self.test_channel = get(self.csua_guild.channels, id=DEBUG_CHANNEL_ID)
            self.hoser_role = get(self.csua_guild.roles, id=HOSER_ROLE_ID)
            self.pb_role = get(self.csua_guild.roles, id=CSUA_PB_ROLE_ID)

    async def on_message(self, message):
        author = message.author
        if author == self.user:
            return
        content = message.content.lower()
        channel = message.channel

        if "hkn" in content and "ieee" in content:
            await channel.send("Do I need to retrieve the stick?")
        if "is typing" in content:
            await channel.send("unoriginal")
        if content.count("cpma") >= 2:
            for emoji in emoji_letters("wtfiscpma"):
                await message.add_reaction(emoji)
        elif "based" in content:
            for emoji in emoji_letters("based"):
                await message.add_reaction(emoji)
            await message.add_reaction("😎")
        elif "tree" in content or "stanford" in content or "stanfurd" in content:
            emoji = unicodedata.lookup(
                "EVERGREEN TREE"
            )  # todo: add official <:tree:744335009002815609>
            await message.add_reaction(emoji)
        elif "drip" in content or "👟" in content or "🥵" in content:
            for emoji in emoji_letters("drip"):
                await message.add_reaction(emoji)
            await message.add_reaction("👟")
        elif "oski" in content:
            for emoji in emoji_letters("oski"):
                await message.add_reaction(emoji)
            await message.add_reaction("😃")
            await message.add_reaction("🐻")
        if content.startswith("!xkcd"):
            # Validate "!xkcd" command
            if xkcd.is_valid_xkcd_command(content):
                await xkcd.get_xkcd(message)
            else:
                await channel.send(
                    "Please ensure that your command is properly formatted. "
                    "Type `!xkcd --help` for more information."
                )
        if content.startswith("!figlet "):
            text = content.split(" ", 1)[1]
            if len(text) > 200:
                await channel.send("!figlet: Message too long")
                return
            formatted = figlet_format(text)
            # Discord has a 2000 character limit
            if len(formatted) > 1994:
                await channel.send("!figlet: Message too long")
                return
            await channel.send(f"```{formatted}```")

        if content.startswith("!cowsay "):
            await cowsay.handle(message)

        if content.startswith("!c4") or content.startswith("!connectfour"):
            await connect4.on_message(self, message)

        if channel == author.dm_channel:
            if content.startswith("!verify"):
                if len(content.split()) > 1:
                    arg = content.split()[1]
                    try:
                        validate_email(arg)
                        if arg.endswith("berkeley.edu"):
                            await author.send(
                                f"A verification email has been sent to {arg}"
                            )
                            await self.test_channel.send(
                                f"{author.name}#{author.discriminator} was sent verification email"
                            )
                            send_verify_mail(
                                arg, author.name + "#" + author.discriminator
                            )
                        else:
                            await channel.send(f"{arg} is not a berkeley email.")
                    except ValidationError as e:
                        await channel.send(f"{arg} is not a valid email. Details: {e}")
                else:
                    await channel.send(
                        "No email entered. Example: `!verify oski@berkeley.edu`"
                    )

            elif content.startswith("!dm"):
                ## SPAGHETTTTI
                """
                !dm <user_id> <message>
                TODO: refactor multiple exception groups
                TODO: refactor to use discord.py's built-in error handling (thanks copilot)
                """
                args = content.split(maxsplit=2)
                if len(args) < 3:
                    await channel.send("!dm: Too few arguments")
                    return

                try:
                    from_member = await self.csua_guild.fetch_member(message.author.id)
                    to_member = await self.csua_guild.fetch_member(int(args[1]))

                    if self.pb_role in from_member.roles:
                        await to_member.send(args[2])
                    else:
                        await channel.send("!dm: Not PB, action forbidden.")
                        return
                except NotFound as e:
                    await channel.send("!dm: user not found!")
                except Forbidden as e:
                    await channel.send("!dm: forbidden request returned!")
                except HTTPException as e:
                    await channel.send("!dm: fetching user failed")
                except Exception as e:
                    await channel.send(f"!dm: {e} generic_exception")

    async def on_raw_reaction_add(self, event):
        await connect4.on_raw_reaction_add(self, event)

    async def on_member_join(self, member):
        msg = await member.send(
            "Welcome to the CSUA Discord server! First, read the rules in #landing-zone. "
            "Thumbs up this message if you agree."
        )
        await self.test_channel.send(f"Sent initial discord message to {member}")

        def check_thumb(react, _):
            return react.message == msg and str(react.emoji) == "👍"  # thumbs

        await self.wait_for("reaction_add", check=check_thumb)
        await self.test_channel.send(f"{member} read rules")

        await member.send(
            "Verify your berkeley.edu email to gain access to the server! "
            "Type `!verify` in this DM plus your email, like so: `!verify oski@berkeley.edu`. "
            "Please contact a moderator if you encounter any issues."
        )


def emoji_letters(chars):
    return [unicodedata.lookup(f"REGIONAL INDICATOR SYMBOL LETTER {c}") for c in chars]


class CSUABot:
    """
    Wraps CSUAClient by abstracting thread and event loop logic.

    All the discord.Client coroutines must be called using
    `asyncio.run_coroutine_threadsafe` because the client is running inside an
    event loop in a separate thread. Event loops are one per-thread, and Django
    can't handle async code, so a separate thread is used instead.

    CSUABot.thread is started in apps/csua_backend/wsgi.py, so that it doesn't
    run during other django commands such as migrate, test etc.
    """

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start, daemon=True)

    def _start(self):
        asyncio.set_event_loop(self.loop)
        self.client = CSUAClient(intents=intents)
        try:
            self.loop.run_until_complete(self.client.start(TOKEN))
        finally:
            self.loop.run_until_complete(self.client.logout())
            self.loop.close()

    def promote_user_to_hoser(self, tag):
        if not hasattr(self.client, "csua_guild"):
            client = self.client
            print(client)
        member = self.client.csua_guild.get_member_named(tag)
        if member:
            asyncio.run_coroutine_threadsafe(
                member.add_roles(self.client.hoser_role), self.loop
            ).result(TIMEOUT_SECS)
            asyncio.run_coroutine_threadsafe(
                self.client.test_channel.send(f"{tag} verified"), self.loop
            ).result(TIMEOUT_SECS)
            return True
        return False

    def event_announcement(self):
        print("Announcements Thread started...")

        times_msg = {
            AnnouncementType.WEEK: "NEXT WEEK",
            AnnouncementType.TODAY: "TODAY",
            AnnouncementType.TOMORROW: "TOMORROW",
            AnnouncementType.HOUR: "IN 1 HOUR",
            AnnouncementType.B_TIME: "NOW",
        }

        def announcer(time_delta):
            events = get_events_in_time_delta(time_delta)

            if events:
                msg = f"**What's happening {times_msg[time_delta]}**"
                asyncio.run_coroutine_threadsafe(
                    self.client.get_channel(ANNOUNCEMENTS_CHANNEL_ID).send(msg),
                    self.loop,
                ).result(TIMEOUT_SECS)
                print("Sending: ", time_delta)  # debugging

                send_embed(events)

        def send_embed(events):
            for event in events:
                embed = discord.Embed(
                    title=event.name,
                    description=event.description,
                    colour=discord.Colour.red(),
                )
                embed.add_field(
                    name="Starts", value=event.get_start_date_and_time_string()
                )
                embed.add_field(name="Ends", value=event.get_end_date_and_time_string())
                if event.link:
                    embed.add_field(name="Link", value=event.link, inline=False)
                asyncio.run_coroutine_threadsafe(
                    self.client.get_channel(ANNOUNCEMENTS_CHANNEL_ID).send(embed=embed),
                    self.loop,
                ).result(TIMEOUT_SECS)

        if DEBUG:
            schedule.every(10).seconds.do(partial(announcer, AnnouncementType.WEEK))
            schedule.every(10).seconds.do(partial(announcer, AnnouncementType.TOMORROW))
            schedule.every(10).seconds.do(partial(announcer, AnnouncementType.TODAY))
            schedule.every(10).seconds.do(partial(announcer, AnnouncementType.HOUR))
            schedule.every(10).seconds.do(partial(announcer, AnnouncementType.B_TIME))
        else:
            schedule.every().sunday.at("17:00").do(
                partial(announcer, AnnouncementType.WEEK)
            )
            schedule.every().day.at("08:00").do(
                partial(announcer, AnnouncementType.TOMORROW)
            )
            schedule.every().day.at("08:00").do(
                partial(announcer, AnnouncementType.TODAY)
            )
            schedule.every().hour.do(partial(announcer, AnnouncementType.HOUR))
            schedule.every(10).minutes.do(partial(announcer, AnnouncementType.B_TIME))

        while True:
            schedule.run_pending()
            time.sleep(5)


if TOKEN:
    csua_bot = CSUABot()
else:
    csua_bot = None
