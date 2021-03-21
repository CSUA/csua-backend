"""
I wasn't able to find documentation on mocking LDAP servers that had good exaples, so I found
https://github.com/StackFocus/PostMaster/blob/master/tests/ad/test_ad_class.py
Which I based some of this code off of
--robertquitt
"""
import os
import unittest
from datetime import datetime

import ldap3
from django.conf import settings
from django.test import TestCase

import apps.ldap.utils as utils
from apps.ldap.test_helpers import LDAPTestCase

from .utils import NEWUSER_DN


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

    def test_create_new_user_and_delete(self):
        max_uid = utils.get_max_uid()
        self.assertEquals(max_uid, 31337)

        success, uid_num = utils.create_new_user(
            "pnunez1",
            "Phillip E. Nunez",
            "pnunez1@berkeley.edu",
            3116969,
            "il0vedangengdg!",
        )
        self.assertTrue(success)
        self.assertEquals(uid_num, 31338)

        self.assertTrue(utils.user_exists("pnunez1"))
        success = utils.delete_user("pnunez1")
        self.assertTrue(success)
        self.assertFalse(utils.user_exists("pnunez1"))

    def test_datetime_to_ldap(self):
        dt = datetime(2021, 2, 13, 15, 8, 37)
        lt = utils.datetime_to_ldap(dt)
        self.assertEquals(lt, "20210213150837Z")

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
