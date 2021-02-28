import asyncio
import json

from django.test import TestCase
from unittest.mock import Mock, MagicMock, call


from .bot import CSUAClient, emoji_letters


class TestCSUAClient(TestCase):
    def setUp(self):
        self.discord_client = CSUAClient()

    def test_reactions(self):
        self.check_message(
            "wtf based and breadpilled???", reactions=emoji_letters("based") + ["😎"]
        )
        self.check_message(cpmacpma, reactions=emoji_letters("wtfiscpma"))
        self.check_message("we drippin", reactions=emoji_letters("drip") + ["👟"])
        self.check_message("oski", reactions = emoji_letters("oski") + ["😃"] + ["🐻"])
        self.check_message("plain ol msg")
        # TODO the rest of them

    def test_replies(self):
        self.check_message(hknieee, replies=["Do I need to retrieve the stick?"])
        # TODO the rest of them ResidentSleeper

    def check_message(self, message, replies=None, reactions=None):
        replies = replies or []
        reactions = reactions or []
        message = Mock(
            content=message, channel=Mock(send=AsyncMock()), add_reaction=AsyncMock()
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.discord_client.on_message(message))
        message.channel.send.assert_has_calls(call(reply) for reply in replies)
        message.add_reaction.assert_has_calls(call(reaction) for reaction in reactions)


class AsyncMock(MagicMock):
    # Backport because we're on Python 3.6, and unittest.mock.AsyncMock is
    # introduced in 3.8
    # Credit: https://stackoverflow.com/a/32498408
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


cpmacpma = """
CPMA! CPMA! Test your CPMA! We've got a lobby waiting for you! CPMA! CPMA! What
do we do? Who's the impost-ah maybe its CPMA.

What did you see when the CPMA was found?

CPMA acting sus when no one was around!

I was with CPMA, I was with CPMA!

Oh, don't you dare CPMA me!

I don't like the sound of that.

CPMA, CPMA! Time to CPMA unanimous vote Dr-Dis- Rreeeee- Spect!
"""
# https://discord.com/channels/784902200102354985/785419328131563530/800241806536081419
# Thank you Alberto

hknieee = """I’d just like to interject for a moment. What you’re refering to
as HKN, is in fact, IEEE-HKN, or as I’ve recently taken to calling it, IEEE
plus HKN. HKN is not an honor society unto itself, but rather another free
component of a fully functioning IEEE system made useful by the HKN office,
baseball bat, and elite t-shirt components comprising a full club as defined by
EECS."""
