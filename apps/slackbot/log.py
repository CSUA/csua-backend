from logging import StreamHandler, Formatter
from .client import webclient

CSUA_PHILBOT_TESTING_CHANNEL_ID = "CCU09PNGL"
CSUA_WEBSITE_UPDATES_CHANNEL_ID = "CG49A3UF8"


class SlackMessageHandler(StreamHandler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        text = self.format(record)
        webclient.chat_postMessage(channel=CSUA_WEBSITE_UPDATES_CHANNEL_ID, text=text)


formatter = lambda: Formatter(
    "*{levelname}* {name}.{funcName}:{lineno} {message}", style="{"
)
