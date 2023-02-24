import datetime
import random
import unicodedata

import discord
from django.db import close_old_connections
from django.utils import timezone

from .models import AniShuffleGame

ANI = [
    "<:ani1:922753586088267776>",
    "<:ani2:922753613430923264>",
    "<:ani3:922753637455904798>",
    "<:ani4:922753662764331018>",
    "<:ani5:922753683274465291>",
    "<:ani6:922753705500098591>",
    "<:ani7:922753727725731840>",
    "<:ani8:922753748583985182>",
    "<:ani9:922753770067197983>",
]

ANICHAMP = "<:AniChamp:800915207722631198>"
SHUFFLE_EMOJI = unicodedata.lookup("TWISTED RIGHTWARDS ARROWS")
LEFT = "⬅️"
UP = "⬆️"
DOWN = "⬇️"
RIGHT = "➡️"


async def init(client, channel, author):
    m = await channel.send(ANI[0])
    close_old_connections()
    game = AniShuffleGame.objects.create(
        message_id=m.id, player_id=author.id, state="1"
    )
    game.save()
    await m.add_reaction(ANICHAMP)


async def get_message(client, event):
    """
    Have a separate message function in order to keep latency low by avoiding
    calls to client.fetch_channel and client.fetch_message
    """
    message = discord.utils.find(
        lambda m: m.id == event.message_id, client.cached_messages
    )
    if message is None:
        message = message_cache.get(event.message_id, None)
    if message is None:
        channel = await client.fetch_channel(event.channel_id)
        message = await channel.fetch_message(event.message_id)
        message_cache[message.id] = message
    return message


message_cache = {}


async def on_raw_reaction_add(client, event):
    if event.user_id == client.user.id:
        # Ignore philbot's own reactions
        return

    if event.emoji.name not in [LEFT, RIGHT, UP, DOWN, SHUFFLE_EMOJI, "AniChamp"]:
        # Ignore irrelevant emojis
        return

    close_old_connections()
    game = AniShuffleGame.objects.filter(message_id=event.message_id).first()

    if not game:
        return

    if event.user_id != game.player_id:
        # Unauthorized
        return

    message = await get_message(client, event)
    new_state = await game_step(game, event, client, message)

    if game.state == new_state or solved(game.state):
        await message.remove_reaction(event.emoji, event.member)
        return

    if len(game.state) == 9:
        game.moves += 1

    game.state = new_state
    game.save()
    new_message = state_to_message(new_state)
    await message.edit(content=new_message)

    if solved(new_state):
        now = timezone.now()
        game.end_time = now
        game.save()
        time = now - game.start_time
        await message.channel.send(
            f"Congrats {event.member}, you are now an AniChamp {ANICHAMP}!\n"
            f"Time: {str(time)[:-3]} Moves: {game.moves} Shuffle Depth: {game.shuffle_depth}"
        )

    await message.remove_reaction(event.emoji, event.member)


async def game_step(game, event, client, message):
    state = game.state
    if event.emoji.name == "AniChamp":
        if len(state) < 9:
            state += str(int(state[-1]) + 1)
        if len(state) > 8:
            await message.remove_reaction(ANICHAMP, client.user)
            await message.add_reaction(SHUFFLE_EMOJI)
    elif event.emoji.name == SHUFFLE_EMOJI and game.state == "123456789":
        state, depth = shuffle("123456780")
        game.shuffle_depth = depth
        await message.remove_reaction(SHUFFLE_EMOJI, client.user)
        for emoji in [LEFT, DOWN, UP, RIGHT]:
            await message.add_reaction(emoji)
    elif event.emoji.name in [UP, LEFT, RIGHT, DOWN]:
        state = swap(state, event.emoji.name)

    return state


def solved(state):
    return state == "123456780"


def flip_horizontal(state):
    board = list(state)
    for a, b in [(0, 2), (3, 5), (6, 8)]:
        board[a], board[b] = board[b], board[a]
    return "".join(board)


def transpose(state):
    board = list(state)
    for a, b in [(1, 3), (2, 6), (5, 7)]:
        board[a], board[b] = board[b], board[a]
    return "".join(board)


def swap(state, direction):
    if direction == LEFT:
        state = swap_left(state)
    elif direction == RIGHT:
        state = flip_horizontal(state)
        state = swap_left(state)
        state = flip_horizontal(state)
    elif direction == UP:
        state = transpose(state)
        state = swap_left(state)
        state = transpose(state)
    elif direction == DOWN:
        state = transpose(state)
        state = flip_horizontal(state)
        state = swap_left(state)
        state = flip_horizontal(state)
        state = transpose(state)
    return state


def swap_left(state):
    pos = state.index("0")
    if pos in [0, 3, 6]:
        return state
    board = list(state)
    board[pos], board[pos - 1] = board[pos - 1], board[pos]
    return "".join(board)


def shuffle(state, steps=100):
    states = [state]
    for i in range(steps):
        state = swap(state, random.choice([UP, DOWN, LEFT, RIGHT]))
        if state == states[-1]:
            pass
        elif len(states) >= 2 and state == states[-2]:
            states.pop()
        else:
            states.append(state)
    return state, len(states)


def state_to_message(state):
    board = [ANICHAMP if i == "0" else ANI[int(i) - 1] for i in state]
    if len(board) > 3:
        board[3] = "\n" + board[3]
    if len(board) > 6:
        board[6] = "\n" + board[6]
    return "".join(board)
