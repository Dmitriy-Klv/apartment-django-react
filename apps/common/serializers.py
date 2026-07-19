from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    """Standard error payload returned by validation and permission failures."""

    detail = serializers.CharField()
