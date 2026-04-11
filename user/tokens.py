from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Token generator for account email verification."""

    def _make_hash_value(self, user, timestamp):
        login_timestamp = ''
        if user.last_login is not None:
            login_timestamp = user.last_login.replace(microsecond=0, tzinfo=None)

        return f"{user.pk}{user.password}{login_timestamp}{timestamp}{user.is_active}{user.email}"

    def check_token(self, user, token):
        if not (user and token):
            return False

        try:
            ts_b36, _hash = token.split('-')
        except ValueError:
            return False

        try:
            timestamp = base36_to_int(ts_b36)
        except ValueError:
            return False

        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                self._make_token_with_timestamp(user, timestamp, secret),
                token,
            ):
                break
        else:
            return False

        timeout_seconds = getattr(settings, 'EMAIL_VERIFICATION_TIMEOUT', 60 * 60 * 24)
        if (self._num_seconds(self._now()) - timestamp) > timeout_seconds:
            return False

        return True


email_verification_token_generator = EmailVerificationTokenGenerator()
