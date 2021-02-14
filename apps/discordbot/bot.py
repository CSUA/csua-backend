import logging
import threading
import asyncio
import unicodedata
import requests
from re import findall
from bs4 import BeautifulSoup
from decouple import config
import discord
from discord.utils import get
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .utils import send_verify_mail

intents = discord.Intents.all()
intents.presences = False

TOKEN = config("DISCORD_TOKEN", default="")
CSUA_GUILD_ID = config("TEST_GUILD", default=784902200102354985, cast=int)
CSUA_PHILBOT_CLIENT_ID = config("BOT_ID", default=737930184837300274, cast=int)
HOSER_ROLE_ID = config("TEST_ROLE", default=785418569412116513, cast=int)  # Verified
DEBUG_CHANNEL_ID = config("DEBUG_CHANNEL", default=788989977794707456, cast=int)
TIMEOUT_SECS = 10
VALID_XKCD_COMMANDS = ["-random", "-r", "-help", "-h", "-issue", "-i"]
XKCD_RANDOM_URL = "https://c.xkcd.com/random/comic/"
XKCD_HELP_MSG = "```!xkcd help\n" + ("-" * 50) + "\n-help (-h)  /  Displays help for the '!xkcd' command.\n" \
                "-random (-r)  /  Displays a random XKCD issue.\n-issue (-i) #  /  Displays a specific XKCD issue.```"
XKCD_HOME_URL = "https://xkcd.com/"

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
            # if self.csua_guild is not None and self.test_channel is not None and self.hoser_role is not None:
            #     await self.test_channel.send("booting up successfully into phillip_debug channel")

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
        if "hkn" in msg and "ieee" in msg:
            await message.channel.send("Do I need to retrieve the stick?")
        if "is typing" in msg:
            await message.channel.send("unoriginal")
        if msg.count("cpma") >= 2:
            for emoji in emoji_letters("wtfiscpma"):
                await message.add_reaction(emoji)
        elif "based" in msg:
            for emoji in emoji_letters("based"):
                await message.add_reaction(emoji)
            await message.add_reaction("😎")
        elif "tree" in msg or "stanford" in msg or "stanfurd" in msg:
            emoji = unicodedata.lookup(
                "EVERGREEN TREE"
            )  # todo: add official <:tree:744335009002815609>
            await message.add_reaction(emoji)
        elif "drip" in msg or "👟" in msg or "🥵" in msg:
            for emoji in emoji_letters("drip"):
                await message.add_reaction(emoji)
            await message.add_reaction("👟")
        if "!xkcd" in msg:
            # Validate "!xkcd" command
            if is_valid_xkcd_command(msg):
                await get_xkcd(message)
            else:
                await message.channel.send("Please ensure that your command is properly formatted. "
                                           "Type `!xkcd -help` for more information.")



    async def on_member_join(self, member):
        msg = await member.send(
            "Welcome to the CSUA discord server! First, read the rules in #landing-zone. Thumbs up this message if you agree"
        )
        await self.test_channel.send(f"Sent initial discord message to {member}")

        def check_thumb(react, _):
            return react.message == msg and str(react.emoji) == "👍"  # thumbs

        await self.wait_for("reaction_add", check=check_thumb)
        await self.test_channel.send(f"{member} read rules")
        await member.send(
            "Verify your berkeley.edu email to gain access. First, pleast type your email. Please contact a moderator if you have any issues."
        )

        await self.test_channel.send(f"{member} was prompted for email")
        await self.verify_member_email(member)
        if self.is_phillip:
            await self.test_channel.send(f"{member} was sent registration email")


def emoji_letters(chars):
    return [unicodedata.lookup(f"REGIONAL INDICATOR SYMBOL LETTER {c}") for c in chars]


def is_valid_xkcd_command(msg):
    """ Returns whether msg contains an valid request. """

    arguments = msg.split()
    if len(arguments) > 3 or len(arguments) < 2:
        return False
    elif arguments[1] in VALID_XKCD_COMMANDS:
        if arguments[1] == VALID_XKCD_COMMANDS[4] or arguments[1] == VALID_XKCD_COMMANDS[5]:
            return len(arguments) == 3 and arguments[2].isdigit()
        else:
            return len(arguments) == 2
    else:
        return False


async def get_xkcd(message):
    """
    Displays either a random XKCD comic, a specific issue, or the '!xkcd' help panel.
    Assumes that a valid command is contained within msg (checked by is_valid_xkcd_command(String)).
    """
    msg = message.content.lower().split();
    cmd = msg[1]
    if cmd == VALID_XKCD_COMMANDS[0] or cmd == VALID_XKCD_COMMANDS[1]:
        await get_random_xkcd(message)
    elif cmd == VALID_XKCD_COMMANDS[2] or cmd == VALID_XKCD_COMMANDS[3]:
        await message.channel.send(XKCD_HELP_MSG)
    elif cmd == VALID_XKCD_COMMANDS[4] or cmd == VALID_XKCD_COMMANDS[5]:
        await get_xkcd_issue(message, msg[2])


async def get_xkcd_issue(message, issue):
    """ Displays the specific XKCD issue requested. """
    soup = get_url_soup(XKCD_HOME_URL + str(issue) + "/")
    if soup:
        comic_info = get_xkcd_from_soup(soup)
        if comic_info:
            await display_xkcd(message, comic_info)
            return
    await message.channel.send("Sorry, I couldn't find that issue right now. Please try again later.")


async def get_random_xkcd(message):
    """ Displays a random xkcd comic. """
    soup = get_url_soup(XKCD_RANDOM_URL)
    if soup:
        comic_info = get_xkcd_from_soup(soup)
        if comic_info:
            await display_xkcd(message, comic_info)
            return
    await message.channel.send("Sorry, I couldn't find anything right now. Please try again later.")


async def display_xkcd(message, comic):
    """ Displays the contents of the xkcd comic. """
    await message.channel.send("Title: " + str(comic["title"]))
    await message.channel.send("Issue: " + "#" + str(comic["issue"]))
    await message.channel.send("Description: *" + str(comic["image_text"]) + "*")
    await message.channel.send(str(comic["image_url"]))


def get_xkcd_from_soup(soup):
    """ Returns a dictionary containing the XKCD info. None if data cannot be parsed. """
    info = {}
    try:
        # TODO: Fix TypeError issue where "comic_soup.find("meta", property = "og:url")" returns None.
        info["url"] = soup.find("meta", property = "og:url")["content"]
        info["issue"] = [int(element) for element in findall(r'\d+', info["url"])][0]
        info["title"] = soup.find("meta", property = "og:title")["content"]
        info["image_url"] = "https:" + soup.find(id="comic").img["src"]
        info["image_text"] = soup.find(id="comic").img["title"]
        return info
    except TypeError:
        return None


def get_url_soup(url):
    """ Returns the soup content of the requested url. None if url cannot be reached."""
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup
    except requests.exceptions.ConnectionError:
        return None


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
        self.running = True
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
        if not hasattr(self.client, "csua_guild"):
            client = self.client
            print(client)
        member = self.client.csua_guild.get_member_named(tag)
        if member:
            asyncio.run_coroutine_threadsafe(
                member.add_roles(self.client.hoser_role), self.loop
            ).result(TIMEOUT_SECS)
            asyncio.run_coroutine_threadsafe(
                self.client.test_channel.send(f"verified {tag}"), self.loop
            ).result(TIMEOUT_SECS)
            return True
        return False


if TOKEN:
    csua_bot = CSUABot()
else:
    csua_bot = None
