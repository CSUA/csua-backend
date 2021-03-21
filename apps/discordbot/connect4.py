import asyncio
import threading
import unicodedata

import discord

from .models import ConnectFourGame

# Some emoji aren't in unicodedata, so the literal emoji are here
BLUE_SQUARE = "🟦"
NUMBERS_PLAINTEXT = [f"[{i}]" for i in range(7)]
NUMBERS_EMOJI = [f"{i}\N{COMBINING ENCLOSING KEYCAP}" for i in range(7)]
RED_CIRCLE = unicodedata.lookup("LARGE RED CIRCLE")
YELLOW_CIRCLE = "🟡"
RED = "R"
YELLOW = "Y"
BLUE = "_"
BELL = unicodedata.lookup("BELL")
DOWN_ARROW = unicodedata.lookup("DOWNWARDS BLACK ARROW")
DOWN_ARROW_2 = "⬇️"


async def on_message(client, message):
    args = message.content.split(" ")
    if len(args) != 2 or len(message.mentions) != 1:
        await message.channel.send("Usage: !connectfour @opponent")
        return
    opponent_id = message.mentions[0].id
    new_board = Board.new(player1=message.author, player2=message.mentions[0])
    m = await message.channel.send(new_board.get_message())
    await add_reaccs(m)
    game = ConnectFourGame.objects.create(
        message_id=m.id,
        player1=message.author.id,
        player2=opponent_id,
        state=new_board.get_state(),
    )


async def add_reaccs(message):
    for num in NUMBERS_EMOJI:
        await message.add_reaction(num)
    await message.add_reaction(DOWN_ARROW)
    await message.add_reaction(BELL)


async def handle_event(client, game, event, message):
    is_player1 = game.player1 == event.user_id
    is_player2 = game.player2 == event.user_id
    if game.winner or not (is_player1 or is_player2):
        return
    if event.emoji.name in [DOWN_ARROW, DOWN_ARROW_2]:
        new_message = await message.channel.send(message.content)
        await message.delete()
        await add_reaccs(new_message)
        game.message_id = new_message.id
        game.save()
        return
    if event.emoji.name == BELL:
        user = await client.fetch_user(
            game.player1 if game.is_player1_turn else game.player2
        )
        dm_channel = user.dm_channel
        if not dm_channel:
            dm_channel = await user.create_dm()
        await dm_channel.send(f"It's your turn in connect 4!: {message.jump_url}")
        return
    if event.emoji.name in NUMBERS_EMOJI:
        column = NUMBERS_EMOJI.index(event.emoji.name)
        board = Board.from_state(game.state)
        color = RED if game.is_player1_turn else YELLOW
        if board.try_move(column, color):
            game.winner = board.get_winner()
            game.is_player1_turn = not game.is_player1_turn
            user = await client.fetch_user(
                game.player1 if game.is_player1_turn else game.player2
            )
            if game.winner:
                winner_user = await client.fetch_user(
                    game.player1 if game.winner == 1 else game.player2
                )
                color = RED if game.winner == 1 else YELLOW
                board.set_win_footer(winner_user, color)
            else:
                color = RED if game.is_player1_turn else YELLOW
                board.set_footer(user, color)
            game.state = board.get_state()
            game.save()
            await message.edit(content=board.get_message())


async def on_raw_reaction_add(client, event):
    try:
        if event.user_id != client.user.id and (
            event.emoji.name in NUMBERS_EMOJI
            or event.emoji.name in [DOWN_ARROW, DOWN_ARROW_2, BELL]
        ):
            channel = await client.fetch_channel(event.channel_id)
            message = await channel.fetch_message(event.message_id)
            game = ConnectFourGame.objects.get(message_id=event.message_id)
            await handle_event(client, game, event, message)
            try:
                await message.remove_reaction(event.emoji.name, event.member)
            except discord.errors.NotFound:
                pass
    except ConnectFourGame.DoesNotExist:
        pass


class Board:
    @staticmethod
    def new(player1, player2):
        b = Board()
        b.header = (
            f"Connect Four game between {player1.mention}({RED}) "
            f"and {player2.mention}({YELLOW})"
        )
        b.rows = [BLUE * 7 for _ in range(6)]
        b.number_line = "".join(NUMBERS_PLAINTEXT)
        b.set_footer(player1, RED)
        return b

    @staticmethod
    def from_state(state):
        b = Board()
        lines = state.split("\n")
        b.header = lines[0]
        b.rows = lines[1:7]
        b.number_line = lines[7]
        b.footer = lines[8]
        return b

    def set_footer(self, user: discord.User, color):
        self.footer = f"{color} {user.mention} to move"

    def set_win_footer(self, user: discord.User, color):
        self.footer = f"{color} {user.mention} won!"

    def get_state(self):
        """Serialize this Board object a string to store in the Game.state field"""
        return "\n".join([self.header] + self.rows + [self.number_line, self.footer])

    def get_message(self):
        """Get a string to display this Board to the user via Discord message"""
        message = (
            self.get_state()
            .replace(BLUE, BLUE_SQUARE)
            .replace(RED, RED_CIRCLE)
            .replace(YELLOW, YELLOW_CIRCLE)
        )
        for plaintext, emoji in zip(NUMBERS_PLAINTEXT, NUMBERS_EMOJI):
            message = message.replace(plaintext, emoji)
        return message

    def try_move(self, column, color):
        valid_move = False
        for i in range(5, -1, -1):
            if self.rows[i][column] == BLUE:
                row = list(self.rows[i])
                row[column] = color
                self.rows[i] = "".join(row)
                return True
        return False

    def get_winner(self):
        rows = self.rows
        columns = ["".join(rows[r][c] for r in range(6)) for c in range(7)]
        diagonals = []
        for offset in range(-2, 4):
            diagonals.append(
                "".join(rows[i][offset + i] for i in range(6) if 0 <= offset + i < 7)
            )
            diagonals.append(
                "".join(
                    rows[5 - i][offset + i] for i in range(6) if 0 <= offset + i < 7
                )
            )
        red_win = RED * 4
        yellow_win = YELLOW * 4
        if any(red_win in check for check in rows + columns + diagonals):
            return 1
        if any(yellow_win in check for check in rows + columns + diagonals):
            return 2
        return None
