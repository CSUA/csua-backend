from django.utils.crypto import salted_hmac
from django.utils.http import int_to_base36
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

from apps.ldap.utils import get_user_hashed_password

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):

        # This uses the old hashed password and timestamp as a hash value
        # so that 1. you manage the time and 2. when you change the password
        # it becomes invalidated

        return (
            six.text_type(get_user_hashed_password(user)) + six.text_type(timestamp)
        )
    
    def _make_token_with_timestamp(self, user, timestamp):
        ts_b36 = int_to_base36(timestamp)

        hash = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, timestamp),
        ).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)

account_activation_token = AccountActivationTokenGenerator()
