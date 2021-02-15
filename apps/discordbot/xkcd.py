import requests
from bs4 import BeautifulSoup
from re import findall

XKCD_HOME_URL = "https://xkcd.com/"
XKCD_RANDOM_URL = "https://c.xkcd.com/random/comic/"
XKCD_HELP_MSG = f"""
```!xkcd command help
{"-" * 50}
-help (-h)  /  Displays help for the '!xkcd' command.
-random (-r)  /  Displays a random XKCD issue.
-issue (-i) #  /  Displays a specific XKCD issue.```
"""
VALID_XKCD_COMMANDS = ["-random", "-r", "-help", "-h", "-issue", "-i"]


def is_valid_xkcd_command(msg):
    """ Returns whether msg contains an valid request. """

    arguments = msg.split()
    if len(arguments) > 3 or len(arguments) < 2:
        return False
    elif arguments[1] in VALID_XKCD_COMMANDS:
        if arguments[1] == "-issue" or arguments[1] == "-i":
            return len(arguments) == 3 and arguments[2].isdigit()
        else:
            return len(arguments) == 2
    else:
        return False


async def display_invalid_command(message):
    """ Displays the prompt for an invalid entry. """
    await message.channel.send("Please ensure that your command is properly formatted. Type `!xkcd -help` for more information.")


async def get_xkcd(message):
    """
    Displays either a random XKCD comic, a specific issue, or the '!xkcd' help panel.
    Assumes that a valid command is contained within msg (checked by is_valid_xkcd_command(String)).
    """
    msg = message.content.lower().split();
    cmd = msg[1]
    if cmd == "-random" or cmd == "-r":
        await get_random_xkcd(message)
    elif cmd == "-help" or cmd == "-h":
        await message.channel.send(XKCD_HELP_MSG)
    elif cmd == "-issue" or cmd == "-i":
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