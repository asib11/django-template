import uuid
import base64
import typing as t
from django.http.request import HttpRequest
from django.core.files.base import ContentFile
from django.db.models.manager import BaseManager
from django.core.files.storage import default_storage
from django.contrib.auth.models import AbstractUser

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.settings import api_settings
from rest_framework.generics import GenericAPIView




class ExtendedFileField(serializers.FileField):
    use_relative: bool = False

    def __init__(self, **kwargs):
        self.use_relative = bool(kwargs.pop('use_relative', False))
        super().__init__(**kwargs)

    def to_representation(self, value):
        if self.use_relative and value:
            path = default_storage.url(value)
            return path
        if value and isinstance(value, str):
            path = default_storage.url(value)
            request: HttpRequest = self.context.get('request')
            if request is not None:
                use_url = getattr(self, 'use_url', api_settings.UPLOADED_FILES_USE_URL)
                if use_url:
                    path = request.build_absolute_uri(path)
            return path

        return super().to_representation(value)

    class Meta:
        swagger_schema_fields = {
            'type': 'string',
            'title': 'File Content',
            'description': 'Content of the file base64 encoded',
            'read_only': False
        }



class ContextMixin:
    def get_context_request(self) -> Request:
        request: Request = self.context.get('request')
        return request

    def get_context_view(self) -> GenericAPIView:
        view: GenericAPIView = self.context.get('view')
        return view

    def get_context_user(self) -> AbstractUser:
        request = self.get_context_request()
        user: AbstractUser = request.user
        return user


class Base64FileField(ExtendedFileField):
    invalid_key = 'invalid'

    def to_internal_value(self, data):
        if isinstance(data, str):
            if ('data:' not in data) or (';base64,' not in data):
                self.fail(self.invalid_key)

            header, data = data.split(';base64,')
            if '/' not in header:
                self.fail(self.invalid_key)

            file_extension = header.split('/')[-1]

            if not file_extension:
                self.fail(self.invalid_key)

            try:
                decoded_file = base64.b64decode(data)
                file_name = "%s.%s" % (str(uuid.uuid4()), file_extension)
                data = ContentFile(decoded_file, name=file_name)
            except Exception:
                self.fail(self.invalid_key)

        return super().to_internal_value(data)


class Base64ImageField(Base64FileField, serializers.ImageField):
    invalid_key = 'invalid_image'


class PrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    _qs_method_name: t.Optional[str] = None
    _qs_method: t.Optional[t.Callable] = None

    def __init__(
        self, *,
        queryset: BaseManager,
        qs_method: t.Optional[t.Callable]=None,
        qs_method_name: t.Optional[str]=None,
        pk_field=None,
        **kwargs
    ):
        self._qs_method_name = qs_method_name
        self._qs_method = qs_method
        kwargs.setdefault('queryset', queryset)
        kwargs.setdefault('pk_field', pk_field)
        super().__init__(**kwargs)

    def _get_qs_method(self) -> t.Optional[t.Callable]:
        qs_method = self._qs_method
        if callable(qs_method):
            return qs_method
        method_name = self._qs_method_name
        if method_name and hasattr(self.root, method_name):
            qs_method = getattr(self.root, method_name)
            if callable(qs_method):
                return qs_method

    def get_queryset(self):
        queryset: BaseManager = getattr(self, 'queryset', None)
        qs_method = self._get_qs_method()
        if qs_method:
            return qs_method(
                queryset=queryset,
                serializer=self
            )
        return super().get_queryset()



class ExtendedImageField(ExtendedFileField, serializers.ImageField):
    pass
