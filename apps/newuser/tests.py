import logging
import os
import unittest
from unittest.mock import Mock, patch

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.ldap.test_helpers import LDAPTestCase
from apps.ldap.utils import email_exists
from apps.newuser.views import newuser_script

from .tokens import newuser_token_generator


class NewUserTest(LDAPTestCase):
    """
    Tests the LDAP code by mocking the CSUA LDAP server.

    """

    # TODO: include tests for failure modes (newuser bind fail, config_newuser
    # fails)
    @patch("subprocess.run")
    def test_remote_newuser_flow(self, subprocess_run):
        logging.disable(logging.CRITICAL)

        url = "/newuser/remote/"
        email = "pnunez2@berkeley.edu"
        resp = self.client.get(url)
        resp = self.client.post(url, {"email": email})
        self.assertContains(resp, "Email sent")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [email])
        token_url = reverse(
            "newuser-remote",
            kwargs={"email": email, "token": newuser_token_generator.make_token(email)},
        )
        full_url = "https://www.csua.berkeley.edu" + token_url
        self.assertIn(full_url, mail.outbox[0].body)

        subprocess_run.return_value.returncode = 0
        self.assertFalse(email_exists(email))
        resp = self.client.get(token_url)
        resp = self.client.post(
            token_url,
            {
                "full_name": "Phillip E. Nunez II",
                "student_id": 3114201612,
                "email": email,
                "username": "pnunez2",
                "password": "okPASSWORD1!",
                "enroll_jobs": False,
                "agree_rules": True,
            },
        )
        self.assertEqual(len(subprocess_run.call_args_list), 1)
        self.assertNotContains(resp, "failed")
        args = subprocess_run.call_args_list[0][0][0]
        self.assertIs(type(args), list)
        for arg in args:
            self.assertIs(type(arg), str)
        self.assertTrue(email_exists(email))

        logging.disable(logging.NOTSET)
