"""
commands.py

functions here should take in the command text and output a response, as
described here:

https://api.slack.com/slash-commands

"""


def help(command_text):
    return {
        "response_type": "ephemeral",
        "text": "Help, I'm stuck in a chatbot factory!",
    }


def finger(command_text):
    return {"response_type": "ephemeral", "text": "Not yet implemented"}


def computers(command_text):
    return {"response_type": "ephemeral", "text": "Not yet implemented"}


COMMANDS = {"/philhelp": help, "/philfinger": finger, "/philcomputers": computers}
