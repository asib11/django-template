from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from user import models as user_models

class IsActiveUser(IsAuthenticated):
    def has_permission(self, request: Request, view):
        has_permission = super().has_permission(request, view)
        if has_permission:
            user: user_models.User = request.user
            return user.status == user_models.STATUS.ACTIVE
        return has_permission


class IsAdminUser(IsActiveUser):
    def has_permission(self, request: Request, view):
        has_permission = super().has_permission(request, view)
        if has_permission:
            user: user_models.User = request.user
            return user.role == user_models.USER_ROLE.ADMIN
        return False






