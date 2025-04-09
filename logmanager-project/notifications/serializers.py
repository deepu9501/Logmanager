"""
Serializers for the notifications app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import NotificationChannel, NotificationTemplate, Notification


class NotificationChannelSerializer(serializers.ModelSerializer):
    """
    Serializer for notification channels.
    """
    class Meta:
        model = NotificationChannel
        fields = [
            'id', 'name', 'type', 'configuration',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for notification templates.
    """
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'subject', 'content',
            'html_content', 'variables', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notifications.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    channel_type = serializers.CharField(source='channel.type', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'username', 'template', 'template_name', 
            'channel', 'channel_name', 'channel_type', 'status',
            'subject', 'content', 'data', 'error_message',
            'created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at'
        ]
        read_only_fields = fields


class NotificationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating notifications with a template and recipients.
    """
    template_name = serializers.CharField(required=True)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    roles = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    data = serializers.DictField(required=False)
    
    def validate(self, data):
        """
        Validate that either user_ids or roles is provided.
        """
        if not data.get('user_ids') and not data.get('roles'):
            raise serializers.ValidationError(
                "Either 'user_ids' or 'roles' must be provided."
            )
            
        # Check if template exists
        from .models import NotificationTemplate
        try:
            NotificationTemplate.objects.get(name=data['template_name'])
        except NotificationTemplate.DoesNotExist:
            raise serializers.ValidationError(
                f"Template with name '{data['template_name']}' does not exist."
            )
            
        return data
    
    def create(self, validated_data):
        """
        Create notifications using the Celery task.
        """
        from .tasks import send_notification
        
        template_name = validated_data.pop('template_name')
        
        # Schedule the notification task
        task = send_notification.delay(template_name, **validated_data)
        
        return {'task_id': task.id, 'status': 'Notification sending initiated'} 