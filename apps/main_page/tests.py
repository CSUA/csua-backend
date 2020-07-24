"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client


class TestPages(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
