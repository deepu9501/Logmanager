"""
Models for the logs app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class LogSource(models.Model):
    """
    Represents a source of log entries (e.g., a server, service, or application).
    """
    name = models.CharField(
        max_length=100,
        help_text=_('Source name (e.g., API Server, Database, Authentication Service)')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Description of the log source')
    )
    
    type = models.CharField(
        max_length=50,
        help_text=_('Type of source (e.g., Server, Application, Service)')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this log source is currently active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('log source')
        verbose_name_plural = _('log sources')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class LogEntry(models.Model):
    """
    Represents an individual log entry from a source.
    """
    SEVERITY_CHOICES = [
        ('INFO', _('Info')),
        ('WARNING', _('Warning')),
        ('ERROR', _('Error')),
        ('CRITICAL', _('Critical')),
    ]

    source = models.ForeignKey(
        LogSource,
        on_delete=models.CASCADE,
        related_name='log_entries',
        help_text=_('Source of the log entry')
    )
    
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        help_text=_('Severity level of the log entry')
    )
    
    message = models.TextField(
        help_text=_('Log message content')
    )
    
    timestamp = models.DateTimeField(
        help_text=_('Time when the log event occurred')
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_('IP address related to the log event')
    )
    
    user_id = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('User ID related to the log event, if applicable')
    )
    
    session_id = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Session ID related to the log event, if applicable')
    )
    
    request_id = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Request ID related to the log event, if applicable')
    )
    
    additional_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Any additional data related to the log event')
    )
    
    classification = models.ForeignKey(
        'classification.LogClassification',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='log_entries',
        help_text=_('Classification of this log entry')
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Category of the log entry')
    )
    
    event_id = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Event ID related to the log entry')
    )
    
    is_read = models.BooleanField(
        default=False,
        help_text=_('Whether this log has been read/acknowledged')
    )
    
    is_flagged = models.BooleanField(
        default=False,
        help_text=_('Whether this log has been flagged for attention')
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_('Additional notes about this log entry')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['severity']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['source']),
            models.Index(fields=['user_id']),
            models.Index(fields=['is_read']),
            models.Index(fields=['is_flagged']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.source.name} - {self.severity}"
    
    @property
    def is_critical(self):
        return self.severity == 'CRITICAL'
    
    @property
    def is_error(self):
        return self.severity == 'ERROR'