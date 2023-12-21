from rest_framework import serializers
from .models import UploadedFile


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ('owner', 'created', 'title', 'file')


class FileListSerializer(serializers.ModelSerializer):
    fields = serializers.ListField()

    class Meta:
        model = UploadedFile
        fields = ('owner', 'created', 'title', 'file', 'fields')


# Альтернативный вариант
# class FileListSerializer(serializers.Serializer):
#     file = UploaderSerializer()
#     fields = serializers.ListField()


class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()
