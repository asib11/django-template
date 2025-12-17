from rest_framework.test import APIClient
from rest_framework.response import Response


class RestAPIClient(APIClient):
    def delete(self, path, data=None, format=None, content_type=None, follow=False, **extra) -> Response:
        return super().delete(path, data, format, content_type, follow, **extra)

    def get(self, path, data=None, follow=False, **extra) -> Response:
        return super().get(path, data, follow, **extra)

    def post(self, path, data=None, format=None, content_type=None, follow=False, **extra) -> Response:
        return super().post(path, data, format, content_type, follow, **extra)

    def patch(self, path, data=None, format=None, content_type=None, follow=False, **extra) -> Response:
        return super().patch(path, data, format, content_type, follow, **extra)

    def put(self, path, data=None, format=None, content_type=None, follow=False, **extra) -> Response:
        return super().put(path, data, format, content_type, follow, **extra)

