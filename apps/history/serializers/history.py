from rest_framework import serializers


class PopularSearchSerializer(serializers.Serializer):
    """Represent an aggregated search keyword with its total popularity."""

    keyword = serializers.CharField()
    total_count = serializers.IntegerField()
