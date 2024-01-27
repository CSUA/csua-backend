import asyncio
import json
from unittest.mock import MagicMock, Mock, call, patch

import cowpy
import discord
from django.test import TestCase
from pyfiglet import figlet_format

from . import connect4
from .bot import CSUAClient, emoji_letters
from .models import ConnectFourGame


class AsyncMock(MagicMock):
    # Backport because we're on Python 3.6, and unittest.mock.AsyncMock is
    # introduced in 3.8
    # Credit: https://stackoverflow.com/a/32498408
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


class TestCSUAClient(TestCase):
    def setUp(self):
        self.discord_client = CSUAClient(intents=discord.Intents.all())
        self.discord_client.oh_check_channel = Mock(return_value=123)

    def test_reactions(self):
        self.check_message(
            "wtf based and breadpilled???", reactions=emoji_letters("based") + ["😎"]
        )
        self.check_message(cpmacpma, reactions=emoji_letters("wtfiscpma"))
        self.check_message("we drippin", reactions=emoji_letters("drip") + ["👟"])
        self.check_message("oski", reactions=emoji_letters("oski") + ["😃"] + ["🐻"])
        self.check_message("plain ol msg")
        # TODO the rest of them

    def test_replies(self):
        self.check_message(hknieee, replies=["Do I need to retrieve the stick?"])
        # TODO the rest of them ResidentSleeper

    def test_figlet(self):
        self.check_message("!figlet test", replies=[f"```{figlet_format('test')}```"])
        self.check_message(
            f"!figlet {'A'*20000}", replies=["!figlet: Message too long"]
        )
        self.check_message(f"!figlet {'A'*199}", replies=["!figlet: Message too long"])

    def test_cowsay(self):
        response = cowpy.cow.Cowacter().milk("test")
        self.check_message("!cowsay test", replies=[f"```{response}```"])

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


class ConnectFourTest(TestCase):
    def setUp(self):
        self.discord_client = CSUAClient(intents=discord.Intents.all())
        self.discord_client.oh_check_channel = Mock(return_value=123)
        self.loop = asyncio.get_event_loop()
        self.mock_opponent_id = 1234
        self.mock_author_id = 1122
        self.mock_game_message_id = 2345
        self.mock_initial_message_id = 5432
        self.mock_player_1 = Mock(
            id=self.mock_author_id, mention=f"<@{self.mock_author_id}>"
        )
        self.mock_player_2 = Mock(
            id=self.mock_opponent_id, mention=f"<@{self.mock_opponent_id}>"
        )
        self.mock_channel = Mock(send=AsyncMock())
        self.mock_initial_message = Mock(
            content=f"!connectfour <@{self.mock_opponent_id}>",
            channel=self.mock_channel,
            mentions=[self.mock_player_2],
            author=self.mock_player_1,
            id=self.mock_initial_message_id,
        )
        self.mock_game_message = Mock(
            add_reaction=AsyncMock(),
            id=self.mock_game_message_id,
            edit=AsyncMock(),
            remove_reaction=AsyncMock(),
        )
        self.mock_channel.send.return_value = self.mock_game_message
        self.mock_channel.fetch_message = AsyncMock(
            side_effect=lambda msg_id: {
                self.mock_initial_message_id: self.mock_initial_message,
                self.mock_game_message_id: self.mock_game_message,
            }[msg_id]
        )
        self.mock_emoji_zero = Mock()
        self.mock_emoji_zero.name = connect4.NUMBERS_EMOJI[0]
        self.mock_emoji_one = Mock()
        self.mock_emoji_one.name = connect4.NUMBERS_EMOJI[1]
        self.mock_fetch_channel = patch.object(
            CSUAClient, "fetch_channel", new_callable=AsyncMock
        ).start()
        self.mock_fetch_channel.return_value = self.mock_channel
        self.mock_fetch_user = patch.object(
            CSUAClient, "fetch_user", new_callable=AsyncMock
        ).start()
        self.mock_fetch_user.side_effect = lambda id: {
            self.mock_author_id: self.mock_player_1,
            self.mock_opponent_id: self.mock_player_2,
        }[id]
        self.mock_bot_user = patch.object(CSUAClient, "user", Mock(id=101010)).start()

    def test_e2e_simple(self):
        """Start a game, play it, and ensure that the game in the database is updated"""
        self.loop.run_until_complete(
            self.discord_client.on_message(self.mock_initial_message)
        )
        event1 = Mock(
            user_id=self.mock_author_id,
            emoji=self.mock_emoji_zero,
            message_id=self.mock_game_message_id,
            member=self.mock_player_1,
        )
        event2 = Mock(
            user_id=self.mock_opponent_id,
            emoji=self.mock_emoji_one,
            message_id=self.mock_game_message_id,
            member=self.mock_player_2,
        )
        for event in [event1, event2, event1, event2, event1, event2, event1]:
            self.loop.run_until_complete(
                self.discord_client.on_raw_reaction_add(event)
            ),
        game = ConnectFourGame.objects.get(message_id=self.mock_game_message_id)
        self.assertEqual(game.winner, 1)
        self.assertEqual(self.mock_game_message.remove_reaction.call_count, 7)

        # Make sure we don't store any emoji in the SQL database, because MySQL can't handle it
        try:
            game.state.encode("ascii")
        except UnicodeDecodeError:
            self.fail("Game state contains non-ascii characters")


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
