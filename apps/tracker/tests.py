"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.http import HttpRequest

import apps.tracker.views as views
import time
import apps.tracker.client as client


class ViewsSanityTest(TestCase):
    fixtures = ["fiber-initial"]

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
        response = views.ping(HttpRequest(), code_text, signature)
        assert response.status_code == 200

    def test_2_index(self):
        response = views.index(HttpRequest())
