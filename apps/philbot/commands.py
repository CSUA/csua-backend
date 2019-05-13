"""
commands.py

functions here should take in the command text and output a (response,
next_command) tuple.

Commands need to return within 3 seconds. Ideally, send an immediate response
to ACK the command, then the results after.

Read here: https://api.slack.com/slash-commands
"""
import json
import re
import shlex
import socket
import subprocess

from django.conf import settings
import requests
from slackclient import SlackClient

from .exceptions import SlackAuthError

SLACK_VERIFICATION_TOKEN = getattr(settings, "SLACK_VERIFICATION_TOKEN", None)
SLACK_BOT_USER_TOKEN = getattr(settings, "SLACK_BOT_USER_TOKEN", None)

Client = SlackClient(SLACK_BOT_USER_TOKEN)
IS_PROD = socket.gethostname() == "tap"


def run_shell_command(command):
    if not IS_PROD:
        command = "ssh soda " + command
    return subprocess.check_output(command, shell=True).decode()


def help(slack_message):
    return (
        {"response_type": "ephemeral", "text": "Help, I'm stuck in a chatbot factory!"},
        help_1,
    )


def help_1(slack_message):
    user_name = slack_message.get("user_name")
    text = ""
    return ({"response_type": "in_channel", "text": ""}, None)


username_regexp = re.compile(r"[A-Za-z0-9.\-_]+")


def finger(slack_message):
    command_text = slack_message.get("text")
    if len(command_text.split()) != 1:
        text = "Usage: /philfinger <user>"
        next = None
    elif not username_regexp.match(command_text):
        text = "Username is invalid :weaver:"
        next = None
    else:
        user = command_text.strip()
        text = "P:hilfinger:ing {}...".format(user)
        next = finger_1
    return {"response_type": "ephemeral", "text": text}, next


def finger_1(slack_message):
    user_id = slack_message.get("user_id")
    payload = {"token": SLACK_BOT_USER_TOKEN, "user": user_id}
    command_text = slack_message.get("text")
    fingerer_user_info = requests.get(
        "https://slack.com/api/users.info", params=payload
    ).json()
    if not fingerer_user_info["ok"]:
        # slack auth failed
        fingerer_user_info = {"user": {"profile": {"display_name": "pnunez"}}}
    fingered_user_info = run_shell_command(
        "finger -m {} | head -n 2".format(command_text)
    )
    if fingered_user_info:
        text = "{} p:hilfinger:ed {}@csua.berkeley.edu: \n```{}```".format(
            fingerer_user_info["user"]["profile"]["display_name"],
            command_text,
            fingered_user_info,
        )
    else:
        text = "{} tried to finger {} but failed!".format(
            fingerer_user_info["user"]["profile"]["display_name"], command_text
        )

    return ({"response_type": "in_channel", "text": text}, None)


def man(slack_message):
    command_text = slack_message.get("text")
    command_text_clean = shlex.quote(command_text)
    man_proc = subprocess.Popen(
        "ssh soda man".split(" ") + [command_text_clean],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    man_response = man_proc.stdout.read().decode()
    if man_response:
        text = "man {}\n{}".format(command_text, man_response)
    else:
        text = "Couldn't find man page. Got: {}.".format(man_proc.stderr.read())
    return ({"response_type": "in_channel", "text": text}, None)


def computers(slack_message):
    text = "https://www.csua.berkeley.edu/computers/"
    return ({"response_type": "ephemeral", "text": text}, None)


COMMANDS = {
    "/philhelp": help,
    "/philfinger": finger,
    "/philcomputers": computers,
    "/man": man,
}
