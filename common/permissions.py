from rest_framework.permissions import *


class IsUserVerified(IsAuthenticated):
    pass

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return request.user and request.user.is_staff

