from django.db.models.manager import BaseManager
from django.contrib.auth.models import AbstractUser
from rest_framework.request import Request
from rest_framework.serializers import Serializer


def filter_by_user(*args, queryset: BaseManager, serializer: Serializer, **kwargs):
    request: Request = serializer.context.get('request')
    user: AbstractUser = request.user
    queryset = queryset.filter(
        user_id=user.pk
    )
    return queryset
