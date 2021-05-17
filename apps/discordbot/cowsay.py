import textwrap

import discord
from cowpy import cow


async def handle(message: discord.Message, cowtype="default"):
    text = message.content.split(" ", 1)[1]
    wrapper = textwrap.TextWrapper(width=40, drop_whitespace=False)
    wrapped_text = "\n".join(wrapper.fill(line) for line in text.split("\n"))
    moo = cow.get_cow(cowtype)()
    cowtext = moo.milk(wrapped_text)
    if len(cowtext) > 1994:
        await message.channel.send("!cowsay: Message too long")
        return
    await message.channel.send(f"```{cowtext}```")
