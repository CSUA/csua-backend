"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from .models import LdapUser
from . import utils


class ModelSanityTest(TestCase):
    def test_a(self):
        user = LdapUser.objects.get(username="lwall")
        self.assertEqual(user.gecos, "Larry Wall")

    def test_b(self):
        realname = utils.uname_to_realname("nweaver")
        self.assertEquals(realname, "Nicholas Weaver")
        realname = utils.uname_to_realname("robertq")
        self.assertEqual(realname, "Robert Quitt")
