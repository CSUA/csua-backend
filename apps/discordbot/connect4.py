import asyncio
import threading
import unicodedata

import discord

from .models import ConnectFourGame

BLUE_SQUARE = "🟦"
RED_CIRCLE = unicodedata.lookup("large red circle")
NUMBERS = [f"{i}\N{COMBINING ENCLOSING KEYCAP}" for i in range(7)]
YELLOW_CIRCLE = "🟡"
BELL = unicodedata.lookup("bell")
DOWN_ARROW = unicodedata.lookup("downwards black arrow")
DOWN_ARROW_2 = "⬇️"


async def on_message(client, message):
    args = message.content.split(" ")
    if len(args) != 2 or len(message.mentions) != 1:
        await message.channel.send("Usage: !connectfour @opponent")
        return
    opponent_id = message.mentions[0].id
    new_game = "\n".join(
        [
            f"Connect Four game between {message.author.mention}({RED_CIRCLE}) "
            f"and {message.mentions[0].mention}({YELLOW_CIRCLE})",
            "\n".join([BLUE_SQUARE * 7 for i in range(6)]),
            "".join(NUMBERS),
            f"{RED_CIRCLE} {message.author.mention} to move",
        ]
    )
    m = await message.channel.send(new_game)
    await add_reaccs(m)
    game = ConnectFourGame.objects.create(
        message_id=m.id, player1=message.author.id, player2=opponent_id, state=new_game
    )


async def add_reaccs(message):
    for num in NUMBERS:
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
    if event.emoji.name in NUMBERS:
        column = NUMBERS.index(event.emoji.name)
        board = Board(game.state)
        color = RED_CIRCLE if game.is_player1_turn else YELLOW_CIRCLE
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
                color = RED_CIRCLE if game.winner == 1 else YELLOW_CIRCLE
                board.footer = f"{color} {winner_user.mention} won!"
            else:
                color = RED_CIRCLE if game.is_player1_turn else YELLOW_CIRCLE
                board.footer = f"{color} {user.mention} to move"
            game.state = board.get_state()
            game.save()
            await message.edit(content=game.state)


async def on_raw_reaction_add(client, event):
    try:
        if event.user_id != client.user.id and (
            event.emoji.name in NUMBERS
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
    def __init__(self, state):
        lines = state.split("\n")
        self.header = lines[0]
        self.rows = lines[1:7]
        self.number_line = lines[7]
        self.footer = lines[8]

    def get_state(self):
        return "\n".join([self.header] + self.rows + [self.number_line, self.footer])

    def try_move(self, column, color):
        valid_move = False
        for i in range(5, -1, -1):
            if self.rows[i][column] == BLUE_SQUARE:
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
        red_win = RED_CIRCLE * 4
        yellow_win = YELLOW_CIRCLE * 4
        if any(red_win in check for check in rows + columns + diagonals):
            return 1
        if any(yellow_win in check for check in rows + columns + diagonals):
            return 2
        return None
