"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client, RequestFactory


class SanitizePaths(TestCase):
    fixtures = ["fiber-initial"]

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_details(self):
        response = self.client.get("/~pnunez/%2E%2E")
        print(response)
