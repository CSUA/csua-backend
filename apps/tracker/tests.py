from django.test import TestCase, Client
from django.http import HttpRequest

import apps.tracker.views as views
import time
import apps.tracker.client as client


class ViewsSanityTest(TestCase):
    def test_1_ping(self):
        env = {
            "delta": 5,
            "username": "pnunez",
            "host": "soda",
            "salt": 123456789,
            "timestamp": int(time.time() * 1000),
        }
        code_text = client.get_code_text(env)
        signature = str(client.signature(code_text))

        c = Client()
        url = "/computers/ping/{0}/{1}".format(code_text, signature)
        response = c.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_2_views(self):
        c = Client()

        response = c.get("/computers/json", follow=True)
        self.assertEquals(response.status_code, 200)

    def test_3_multiple_logins(self):
        env = {
            "delta": 5,
            "username": "pnunez",
            "host": "soda",
            "salt": 123456789,
            "timestamp": int(time.time() * 1000),
        }
        code_text = client.get_code_text(env)
        signature = str(client.signature(code_text))
        c = Client()
        response = c.get(
            "/computers/ping/{0}/{1}".format(code_text, signature), follow=True
        )

        env2 = {
            "delta": 5,
            "username": "pnunez",
            "host": "tap",
            "salt": 123456789,
            "timestamp": int(time.time() * 1000),
        }
        code_text = client.get_code_text(env)
        signature = str(client.signature(code_text))
        c2 = Client()
        response = c2.get(
            "/computers/ping/{0}/{1}".format(code_text, signature), follow=True
        )

        self.assertEqual(response.status_code, 200)
