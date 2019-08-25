import threading
import json
import requests
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from slack import WebClient
from .commands import COMMANDS
from .exceptions import SlackAuthError

SLACK_VERIFICATION_TOKEN = getattr(settings, "SLACK_VERIFICATION_TOKEN", None)
SLACK_BOT_USER_TOKEN = getattr(settings, "SLACK_BOT_USER_TOKEN", None)


Client = WebClient(SLACK_BOT_USER_TOKEN)


class SlackEventAPI(APIView):
    def post(self, request, *args, **kwargs):
        """
        {
            "token": SLACK_VERIFICATION_TOKEN,
            "team_id": "T0395N0DV",
            "api_app_id": "ACVDH591C",
            "event": {
                "type": "message"
                "user": "U40GUFVBP",
                "text": "Event",
                "client_msg_id": "06f856c9-e94e-4b60-bd4e-756d312978be",
                "ts": "1537053174.000100",
                "channel": "CCU09PNGL",
                "event_ts": "1537053174.000100",
                "channel_type": "channel",
            },
            "type": "event_callback",
            "event_id": "EvCU6Y1PT6",
            "event_time": 1537053174,
            "authed_users": ["UCTE40G64", "U40GUFVBP"],
        }
        """
        slack_message = request.data
        if slack_message.get("token") != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if slack_message.get("type") == "url_verification":
            return Response(data=slack_message, status=status.HTTP_200_OK)

        if "event" in slack_message:
            event_message = slack_message.get("event")

            # ignore bot messages
            if event_message.get("subtype") == "bot_message":
                return Response(status=status.HTTP_200_OK)

            # process user's message
            user = event_message.get("user")
            text = event_message.get("text")
            channel = event_message.get("channel")
            bot_text = "Hi <@{}> :wave:".format(user)
            if False and text and "hi" in text.lower():
                Client.api_call(
                    method="chat.postMessage", channel=channel, text=bot_text
                )
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)


class SlackCommandAPI(APIView):
    def post(self, request, *args, **kwargs):
        """
        {
            "token": [SLACK_VERIFICATION_TOKEN],
            "team_id": ["T0395N0DV"],
            "team_domain": ["csua"],
            "channel_id": ["CCU09PNGL"],
            "channel_name": ["philbot-testing"],
            "user_id": ["U40GUFVBP"],
            "user_name": ["robertquitt"],
            "command": ["/philhelp"],
            "text": ["a"],
            "response_url": [
                "https://hooks.slack.com/commands/T0395N0DV/435854335809/Qhpc6kky496VUnNk3h6cwW0u"
            ],
            "trigger_id": ["435854335841.3311748471.1df6a484aac29f0fdef3a7b578193fa0"],
        }
        """
        slack_message = request.data
        if slack_message.get("token") != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if slack_message.get("type") == "url_verification":
            return Response(data=slack_message, status=status.HTTP_200_OK)

        command = slack_message.get("command")

        if command in COMMANDS:
            try:
                response, delayed_response = COMMANDS[command](slack_message)
                if delayed_response:
                    response_url = slack_message.get("response_url")
                    t = threading.Thread(
                        target=send_delayed_response,
                        args=[response_url, delayed_response, slack_message],
                    )
                    t.setDaemon(False)
                    t.start()
            except SlackAuthError:
                return Response("Could not access Slack API")
            return Response(response)
        else:
            return Response("Command not recognized: {}".format(command))


def send_delayed_response(response_url, delayed_response, slack_message):
    while delayed_response is not None:
        response, delayed_response = delayed_response(slack_message)
        headers = {"Content-type": "application/json"}
        body = json.dumps(response)
        r = requests.post(response_url, body, headers=headers)
