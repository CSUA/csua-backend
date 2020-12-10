import re
import subprocess
import socket
import shlex

from django.conf import settings

from decouple import config
from slack_bolt import App


username_regexp = re.compile(r"[A-Za-z0-9.\-_]+")

IS_PROD = socket.gethostname() == "tap"

SLACK_BOT_USER_TOKEN = config("SLACK_BOT_USER_TOKEN", default="")
SLACK_SIGNING_SECRET = config("SLACK_SIGNING_SECRET", default="")


def message_based(message, say):
    for reacc in ["b", "a", "five", "e-mail", "id"]:
        app.client.reactions_add(
            channel=message["channel"], timestamp=message["ts"], name=reacc
        )


def event_message(event, say):
    pass


def command_export(ack, say, command):
    ack("gotcha")


def command_help(ack, say, command):
    ack("Help, I'm trapped in a chatbot factory!", response_type="in_channel")


def run_shell_command(command):
    if not IS_PROD:
        command = "ssh soda " + command
    return subprocess.check_output(command, shell=True).decode()


def command_finger(ack, say, command):
    args = command.get("text", "")
    if len(args.split()) != 1:
        ack("Usage: /philfinger <user>")
        return
    elif not username_regexp.match(args):
        ack("Username is invalid :weaver:")
        return
    csua_user = args.strip()
    ack(f"P:hilfinger:ing {csua_user}...")
    slack_user_info = app.client.users_info(user=command["user_id"])
    print(slack_user_info)
    if not slack_user_info["ok"]:
        slack_user_info = {"user": {"profile": {"display_name": "pnunez"}}}
    finger_output = run_shell_command(f"finger -m {csua_user} | head -n 2")
    slack_name = (
        slack_user_info["user"]["profile"]["display_name"]
        or slack_user_info["user"]["name"]
    )
    if finger_output:
        say(
            f"""{slack_name} p:hilfinger:ed {csua_user}@csua.berkeley.edu:
```{finger_output}```""",
            response_type="in_channel",
        )
    else:
        say(f"{slack_name} tried to finger {csua_user} but failed!")


def command_man(ack, say, command):
    command_text = command["text"]
    command_text_clean = shlex.quote(command_text)
    ack("Fetching man page...")
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
    say(text, response_type="in_channel")


if SLACK_BOT_USER_TOKEN and SLACK_SIGNING_SECRET:
    app = App(token=SLACK_BOT_USER_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
    app.message("based")(message_based)
    app.event("message")(event_message)
    app.command("/man")(command_man)
    app.command("/philfinger")(command_finger)
    app.command("/export")(command_export)
    app.command("/help")(command_help)
else:
    app = None
