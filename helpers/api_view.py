import typing as t
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from drf_yasg.utils import swagger_auto_schema


class QueryParamsMixin(GenericAPIView):
    params_serializer: serializers.Serializer
    _params_validated_data: t.Optional[dict] = None

    def get_params(self, *_, partial=True, **kwargs) -> dict:
        if self._params_validated_data is None:
            Serializer = self.params_serializer
            request: Request = self.request
            serializer: serializers.Serializer = Serializer(
                data=request.query_params,
                partial=partial,
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            params = serializer.validated_data
            self._params_validated_data = params
        return self._params_validated_data

    def get_query(self, partial=True, filter_null=True, filter_blank=True) -> dict:
        params = self.get_params(partial=partial)
        query = {}
        for key, value in params.items():
            if filter_null and value is None:
                continue
            if filter_blank and value == '':
                continue
            query[key] = value
        return query


def create_view(request_body: serializers.Serializer, response: serializers.Serializer):
    def wrapper(Class: GenericAPIView):
        class CreateAPIView(Class):
            serializer_class = request_body

            def create(self, request: Request, *args, **kwargs):
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                instance = serializer.instance
                context = self.get_serializer_context()
                data = response(instance, context=context).data
                return Response(data)

            @swagger_auto_schema(
                request_body=request_body,
                responses={
                    200: response
                }
            )
            def post(self, request, *args, **kwargs):
                return super().post(request, *args, **kwargs)

        return CreateAPIView
    return wrapper
