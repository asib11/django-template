from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model



User = get_user_model()



class UsernameAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        """Reject users with is_active=False."""
        return getattr(user, 'is_active', False)


class EmailAuthenticationBackend(UsernameAuthenticationBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None


class EmailRoleAuthenticationBackend(UsernameAuthenticationBackend):
    def authenticate(self, request, email=None, role=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email, role=role)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
