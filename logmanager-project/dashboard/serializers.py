"""
Serializers for the dashboard app.
"""

from rest_framework import serializers
from .models import Dashboard, Widget, SavedQuery


class WidgetSerializer(serializers.ModelSerializer):
    """
    Serializer for dashboard widgets.
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Widget
        fields = [
            'id', 'dashboard', 'type', 'type_display', 'title',
            'configuration', 'position_x', 'position_y', 
            'width', 'height', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardSerializer(serializers.ModelSerializer):
    """
    Serializer for dashboards.
    """
    widgets = WidgetSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'user', 'username', 'name', 'description',
            'is_default', 'layout', 'widgets',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'created_at', 'updated_at']


class SavedQuerySerializer(serializers.ModelSerializer):
    """
    Serializer for saved log queries.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SavedQuery
        fields = [
            'id', 'user', 'username', 'name', 'description',
            'query_params', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'created_at', 'updated_at'] 