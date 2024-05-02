from rest_framework import serializers


class BinaryField(serializers.Field):
    def to_representation(self, value):
        return value.decode("utf-8")

    def to_internal_value(self, data):
        return data.encode("utf-8")
