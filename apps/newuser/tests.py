import unittest

from django.test import TestCase

from . import ldap_bindings

@unittest.skip("These are slow")
class SimpleTest(unittest.TestCase):
    def test_get_max_uid(self):
        max_uid = ldap_bindings.get_max_uid()
        self.assertGreaterEqual(max_uid, 31337)

    def test_auth(self):
        result = ldap_bindings.authenticate("robertq", "wrong")
        self.assertFalse(result)
        result = ldap_bindings.authenticate("nonexistant_user_hopefully", "a")
        self.assertFalse(result)

    def test_is_officer(self):
        result = ldap_bindings.is_officer("robertq")
        # hopefully I'll be an officer forever :3
        self.assertTrue(result)

        result = ldap_bindings.is_officer("dangengdg")
        self.assertFalse(result)

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
