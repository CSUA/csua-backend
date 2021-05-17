from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import salted_hmac
from django.utils.http import int_to_base36

from apps.ldap.utils import get_user_hashed_password


class DiscordTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user)

    def _make_token_with_timestamp(self, user, timestamp):
        ts_b36 = int_to_base36(timestamp)
        print(timestamp)

        hash = salted_hmac(
            self.key_salt, self._make_hash_value(user, timestamp)
        ).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)


discord_token_generator = DiscordTokenGenerator()
