import os
import unittest
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
import ldap3

from .utils import NEWUSER_DN

TEST_NEWUSER_PW = "ilovepnunez"

mock_ldap_server = ldap3.Server.from_definition(
    "",
    os.path.join(settings.BASE_DIR, "fixtures", "csua_ldap_info.json"),
    os.path.join(settings.BASE_DIR, "fixtures", "csua_ldap_schema.json"),
)


class LDAPTestCase(TestCase):
    def setUp(self):
        self.patchers = [
            patch("apps.ldap.utils.LDAP_SERVER", mock_ldap_server),
            patch("apps.ldap.utils.LDAP_CLIENT_STRATEGY", ldap3.MOCK_SYNC),
            patch("apps.ldap.utils.NEWUSER_PW", TEST_NEWUSER_PW),
        ]
        for p in self.patchers:
            p.start()
        with ldap3.Connection(mock_ldap_server, client_strategy=ldap3.MOCK_SYNC) as c:
            c.strategy.entries_from_json(
                os.path.join(settings.BASE_DIR, "fixtures", "csua_ldap_entries.json")
            )
            c.strategy.add_entry(
                "uid=cnunez,ou=People,dc=csua,dc=berkeley,dc=edu",
                {
                    "uid": "cnunez",
                    "cn": "cnunez",
                    "gecos": "C Nunez,cnunez@berkeley.edu",
                    "uidNumber": 420,
                    "userPassword": "pp",
                    "objectClass": ["posixAccount"],
                },
            )
            c.strategy.add_entry(
                "uid=test_user,ou=People,dc=csua,dc=berkeley,dc=edu",
                {
                    "uid": "test_user",
                    "cn": "test_user",
                    "uidNumber": 31337,
                    "userPassword": "test_password",
                    "objectClass": ["posixAccount"],
                },
            )
            c.strategy.add_entry(
                NEWUSER_DN,
                {
                    "uid": "newuser",
                    "userPassword": TEST_NEWUSER_PW,
                    "objectClass": ["posixAccount"],
                },
            )

    def tearDown(self):
        for p in self.patchers:
            p.stop()
