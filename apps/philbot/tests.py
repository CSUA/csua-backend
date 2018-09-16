from django.test import TestCase

# Create your tests here.
from django.test.client import Client, RequestFactory
from django.conf import settings

SLACK_VERIFICATION_TOKEN = getattr(settings, "SLACK_VERIFICATION_TOKEN", None)


class SanityTest(TestCase):
    """
    {
        "token": [SLACK_VERIFICATION_TOKEN
        ],
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

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_command_help(self):
        payload = {
            "token": [SLACK_VERIFICATION_TOKEN],
            "team_id": ["T0395N0DV"],
            "team_domain": ["csua"],
            "channel_id": ["CCU09PNGL"],
            "channel_name": ["philbot-testing"],
            "user_id": ["U40GUFVBP"],
            "user_name": ["robertquitt"],
            "command": ["/philhelp"],
            "text": [""],
            "response_url": [
                "https://hooks.slack.com/commands/T0395N0DV/435854335809/Qhpc6kky496VUnNk3h6cwW0u"
            ],
            "trigger_id": ["435854335841.3311748471.1df6a484aac29f0fdef3a7b578193fa0"],
        }
        # TODO: make this work! --robertquitt
        response = self.client.post("/slack/command")
        print(response)
