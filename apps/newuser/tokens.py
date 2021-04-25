from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import salted_hmac
from django.utils.http import int_to_base36

from apps.ldap.utils import email_exists


class NewUserTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, email, timestamp):
        return str(email) + str(email_exists(email)) + str(timestamp)

    def _make_token_with_timestamp(self, email, timestamp):
        ts_b36 = int_to_base36(timestamp)

        hash = salted_hmac(
            self.key_salt, self._make_hash_value(email, timestamp)
        ).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)


newuser_token_generator = NewUserTokenGenerator()
