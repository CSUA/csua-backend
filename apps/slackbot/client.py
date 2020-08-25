from django.conf import settings
from slack import WebClient

SLACK_BOT_USER_TOKEN = getattr(settings, "SLACK_BOT_USER_TOKEN", None)
webclient = WebClient(token=SLACK_BOT_USER_TOKEN)
