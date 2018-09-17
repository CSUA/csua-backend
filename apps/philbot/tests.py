import json
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

# Create your tests here.
from django.test.client import Client, RequestFactory
from django.conf import settings

SLACK_VERIFICATION_TOKEN = getattr(settings, "SLACK_VERIFICATION_TOKEN", None)


class SlackCommandSanityTest(TestCase):
    """
    Sanity tests for responding to commands. Does not test the delayed
    responses.
    """

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def create_payload(self, command, text=""):
        payload = {
            "token": [SLACK_VERIFICATION_TOKEN],
            "team_id": ["T0395N0DV"],
            "team_domain": ["csua"],
            "channel_id": ["CCU09PNGL"],
            "channel_name": ["philbot-testing"],
            "user_id": ["U40GUFVBP"],
            "user_name": ["robertquitt"],
            "command": [command],
            "text": [text],
            "response_url": [
                "https://hooks.slack.com/commands/T0395N0DV/435854335809/Qhpc6kky496VUnNk3h6cwW0u"
            ],
            "trigger_id": ["435854335841.3311748471.1df6a484aac29f0fdef3a7b578193fa0"],
        }
        return payload

    def check_valid_response(self, response):
        self.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content.decode())
        print(response_content)
        self.assertIn("text", response_content)
        self.assertIn("response_type", response_content)
        self.assertIn(response_content["response_type"], ("in_channel", "ephemeral"))

    def test_command_help(self):
        payload = self.create_payload("/philhelp")
        response = self.client.post("/slack/command/", payload)
        self.check_valid_response(response)

    def test_command_finger(self):
        payload = self.create_payload("/philfinger", "nweaver")
        response = self.client.post("/slack/command/", payload)
        self.check_valid_response(response)
