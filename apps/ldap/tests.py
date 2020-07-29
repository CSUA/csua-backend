"""
I wasn't able to find documentation on mocking LDAP servers that had good exaples, so I found
https://github.com/StackFocus/PostMaster/blob/master/tests/ad/test_ad_class.py
Which I based some of this code off of
--robertquitt
"""
import unittest
import os
from unittest.mock import patch

from django.test import TestCase
from django.conf import settings
import ldap3

from .utils import NEWUSER_DN
import apps.ldap.utils as utils
from apps.ldap.test_helpers import LDAPTestCase


class LdapBindingsTest(LDAPTestCase):
    """
    Tests the LDAP code by mocking the CSUA LDAP server.
    """

    def test_auth(self):
        result = utils.authenticate("test_user", "test_password")
        self.assertTrue(result)
        result = utils.authenticate("test_user", "wrong_password")
        self.assertFalse(result)

    def test_is_officer(self):
        result = utils.is_officer("robertq")
        # hopefully I'll be an officer forever :3
        self.assertTrue(result)

        result = utils.is_officer("dangengdg")
        self.assertFalse(result)

    def test_create_new_user(self):
        max_uid = utils.get_max_uid()
        self.assertEquals(max_uid, 31337)

        success, uid_num = utils.create_new_user(
            "pnunez",
            "Phillip E. Nunez",
            "pnunez@berkeley.edu",
            3116969,
            "il0vedangengdg!",
        )
        self.assertTrue(success)
        self.assertEquals(uid_num, 31338)

        max_uid = utils.get_max_uid()
        self.assertEquals(max_uid, 31338)

    # TODO: finish this
    # def test_password(self):
    #     test_password = "dangengdg is my Friend"
    #     ssha_pw = ldap_bindings.make_password(test_password)
    #     self.assertTrue(ssha_pw.startswith("{SSHA}"))
    #     digest_salt_b64 = ssha_pw[6:]

    #     digest_salt = digest_salt_b64.decode('base64')
    #     digest = digest_salt[:20]
    #     salt = digest_salt[20:]

    #     sha = hashlib.sha1(test_password)
    #     sha.update(salt)

    #     self.assertEquals(digest, sha.digest())
