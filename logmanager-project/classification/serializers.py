"""
Serializers for the classification app.
"""

from rest_framework import serializers
from .models import LogClassification, ClassificationKeyword, ClassificationModel


class ClassificationKeywordSerializer(serializers.ModelSerializer):
    """
    Serializer for classification keywords.
    """
    class Meta:
        model = ClassificationKeyword
        fields = [
            'id', 'classification', 'keyword', 'weight',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LogClassificationSerializer(serializers.ModelSerializer):
    """
    Serializer for log classifications.
    """
    keywords = ClassificationKeywordSerializer(many=True, read_only=True)
    log_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LogClassification
        fields = [
            'id', 'name', 'description', 'priority',
            'color_code', 'notification_enabled', 'pattern',
            'keywords', 'log_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClassificationModelSerializer(serializers.ModelSerializer):
    """
    Serializer for classification models.
    """
    class Meta:
        model = ClassificationModel
        fields = [
            'id', 'name', 'description', 'version',
            'model_file', 'vectorizer_file', 'accuracy',
            'is_active', 'trained_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'model_file', 'vectorizer_file', 'accuracy',
            'trained_at', 'created_at', 'updated_at'
        ] 