"""
commands.py

functions here should take in the command text and output a (response,
next_command) tuple.

Commands need to return within 3 seconds. Ideally, send an immediate response
to ACK the command, then the results after.

Read here: https://api.slack.com/slash-commands
"""
import json
from apps.tracker.views import getComputers
from django.conf import settings
import requests
import subprocess
from slackclient import SlackClient

SLACK_VERIFICATION_TOKEN = getattr(settings, "SLACK_VERIFICATION_TOKEN", None)
SLACK_BOT_USER_TOKEN = getattr(settings, "SLACK_BOT_USER_TOKEN", None)

Client = SlackClient(SLACK_BOT_USER_TOKEN)


def help(slack_message):
    return (
        {"response_type": "ephemeral", "text": "Help, I'm stuck in a chatbot factory!"},
        help_1,
    )


def help_1(slack_message):
    user_name = slack_message.get("user_name")
    text = ""
    return ({"response_type": "in_channel", "text": ""},)


def finger(slack_message):
    command_text = slack_message.get("text")
    if len(command_text.split()) != 1:
        text = "Usage: /philfinger <user>"
        next = None
    else:
        user = command_text.strip()
        text = "Fingering {}...".format(user)
        next = finger_1
    return {"response_type": "ephemeral", "text": text}, next


def finger_1(slack_message):
    # user = slack_message.get("text")
    user_id = slack_message.get("user_id")
    # userinfo = Client.api_call(method="user.info", user=user_id)
    payload = {"token": SLACK_BOT_USER_TOKEN, "user": user_id}
    command_text = slack_message.get("text")
    r = requests.get("https://slack.com/api/users.info", params=payload)
    fingerer_user_info = json.loads(r.text)
    fingered_user_info = subprocess.check_output(
        ["ssh", "soda", "finger", "-m", command_text, "|", "head", "-n", "2"]
    ).decode()
    if fingered_user_info:
        text = "{} `finger`ed {}@csua.berkeley.edu: \n{}".format(
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
    man_response = subprocess.check_output(
        "ssh soda man".split(' ') + [command_text]
    ).decode()
    if man_response:
        text = "man {}\n{}".format(command_text, man_response)
    else:
        text = "No man page exists for {}.".format(command_text)
    return ({"response_type": "in_channel", "text": text}, None)


def computers(slack_message):
    text = "https://www.csua.berkeley.edu:8080/computers/"
    return ({"response_type": "ephemeral", "text": text}, None)


COMMANDS = {"/philhelp": help, "/philfinger": finger, "/philcomputers": computers}
