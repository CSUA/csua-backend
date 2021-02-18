import requests
import discord
import random

HOST = "http://xkcd.com/"
VALID_XKCD_COMMANDS = ["--random", "-r", "--help", "-h", "--issue", "-i", "--current", "-c"]
MAX_ARGUMENT_LENGTH = 3
MIN_ARGUMENT_LENGTH = 2


def is_valid_xkcd_command(msg):
    """ Returns whether msg contains an valid request. """

    arguments = msg.split()
    if len(arguments) > MAX_ARGUMENT_LENGTH or len(arguments) < MIN_ARGUMENT_LENGTH:
        return False
    elif arguments[1] in VALID_XKCD_COMMANDS:
        if arguments[1] == "-issue" or arguments[1] == "-i":
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
    msg = message.content.lower().split()
    cmd = msg[1]
    comic = None
    
    if cmd == "-help" or cmd == "-h":
        await display_help(message)
        return

    if cmd == "--random" or cmd == "-r":
        comic = get_random()
    elif cmd == "--issue" or cmd == "-i":
        comic = get_issue(msg[2])
    elif cmd == "--curent" or cmd == "-c":
        comic = get_current()

    if comic:
        await display(comic, message)
    else:
        await message.channel.send("Sorry, I can't find a comic right now. Please try again later.")


async def display(metadata, msg):
    if metadata:
        embed = discord.Embed(
            title = "#" + str(metadata["num"]) + " - " + metadata["title"],
            description = metadata["alt"],
        )
        embed.set_image(url = metadata["img"])
        await msg.channel.send(embed = embed)

async def display_help(msg):
    embed = discord.Embed(
        title = "'!xkcd' Command Help"
    )
    embed.add_field(name = "--help (-h)", value = "Displays help for the '!xkcd' command.", inline = False)
    embed.add_field(name = "--random (-r)", value = "Displays a random XKCD issue.", inline = False)
    embed.add_field(name = "--issue (-i) #", value = "Displays a specific XKCD issue #.", inline = False)
    embed.add_field(name = "--current (-c)", value = "Displays the current XKCD issue.", inline = False)
    await msg.channel.send(embed = embed)

def get_issue(num):
    url = HOST + str(num) + "/"
    return get_json(url)


def get_current():
    return get_json(HOST)


def get_json(url):
    try:
        return requests.get(url + "info.0.json").json()
    except json.JSONDecodeError:
        return None


def get_random():
    """
    Retrieves the current issue of XKCD, chooses an issue 1 - current issue #, and returns a json object.
    Returns null if an requests error occurs.
    """
    return get_issue(random.randint(1, int(get_current()["num"])))