from rest_framework import serializers

from .models import ProcessedImage


class RemoveBackgroundSerializer(serializers.Serializer):
    file = serializers.FileField()


class ProcessedImageSerializer(serializers.ModelSerializer):
    file = serializers.CharField(source='file.url')
    class Meta:
        models = ProcessedImage
        fields = '__all__'
