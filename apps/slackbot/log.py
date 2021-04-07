from logging import Formatter, StreamHandler

from .client import SLACK_BOT_USER_TOKEN, app

CSUA_PHILBOT_TESTING_CHANNEL_ID = "CCU09PNGL"
CSUA_WEBSITE_UPDATES_CHANNEL_ID = "CG49A3UF8"


class SlackMessageHandler(StreamHandler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        text = self.format(record)
        app.client.chat_postMessage(channel=CSUA_WEBSITE_UPDATES_CHANNEL_ID, text=text)


def formatter():
    return Formatter("*{levelname}* {name}.{funcName}:{lineno} {message}", style="{")


def enabled():
    """Used by apps.csua_backend.settings.LOGGING"""

    def f(record):
        return SLACK_BOT_USER_TOKEN is not None

    return f
