"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

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
        response = c.get("/computers/ping/{0}/{1}".format(code_text, signature))
        self.assertEqual(response.status_code, 200)

    def test_2_views(self):
        c = Client()

        response = c.get("/computers/json")
        self.assertEquals(response.status_code, 200)
        # TODO: check JSON
        # self.assertJSONEqual(response.content)
        # self.assertInHTML("pnunez", response.content)
        # self.assertInHTML("soda", response.conent)

    def test_3_multiple_pings(self):
        pass
