"""
Serializers for the logs app.
"""

from rest_framework import serializers
from .models import LogSource, LogEntry


class LogSourceSerializer(serializers.ModelSerializer):
    """
    Serializer for log sources.
    """
    log_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LogSource
        fields = [
            'id', 'name', 'description', 'type',
            'is_active', 'log_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LogEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for log entries with full details.
    """
    source_name = serializers.CharField(source='source.name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    classification_name = serializers.CharField(source='classification.name', read_only=True)
    
    class Meta:
        model = LogEntry
        fields = [
            'id', 'source', 'source_name', 'severity', 'severity_display',
            'message', 'timestamp', 'ip_address', 'user_id', 'session_id',
            'request_id', 'additional_data', 'classification', 'classification_name',
            'is_read', 'is_flagged', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LogEntryListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing log entries.
    """
    source_name = serializers.CharField(source='source.name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = LogEntry
        fields = [
            'id', 'source', 'source_name', 'severity', 'severity_display',
            'message', 'timestamp', 'is_read', 'is_flagged'
        ]
        read_only_fields = fields


class LogEntryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new log entries.
    """
    class Meta:
        model = LogEntry
        fields = [
            'source', 'severity', 'message', 'timestamp', 
            'ip_address', 'user_id', 'session_id', 'request_id', 
            'additional_data'
        ]


class LogEntryBulkCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating log entries.
    """
    logs = LogEntryCreateSerializer(many=True)
    
    def create(self, validated_data):
        logs_data = validated_data.pop('logs')
        logs = []
        
        for log_data in logs_data:
            logs.append(LogEntry(**log_data))
        
        return LogEntry.objects.bulk_create(logs)


class LogEntryUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating log entries (only certain fields).
    """
    class Meta:
        model = LogEntry
        fields = ['is_read', 'is_flagged', 'notes', 'classification']
        read_only_fields = [] 