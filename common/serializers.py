from dataclasses import dataclass

from rest_framework import serializers


@dataclass
class ResponseObj:
    details: str = ''
    success: bool = True
    code: str = 'SUCCESS'


class ResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    details = serializers.CharField()
    code = serializers.CharField()


