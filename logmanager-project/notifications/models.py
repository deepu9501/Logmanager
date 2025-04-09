"""
Models for the notifications app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class NotificationChannel(models.Model):
    """
    Represents a channel for sending notifications (e.g., email, SMS, webhook).
    """
    class ChannelType(models.TextChoices):
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
        WEBHOOK = 'WEBHOOK', _('Webhook')
        WEBSOCKET = 'WEBSOCKET', _('WebSocket')
    
    name = models.CharField(
        max_length=100,
        help_text=_('Channel name')
    )
    
    type = models.CharField(
        max_length=10,
        choices=ChannelType.choices,
        help_text=_('Type of notification channel')
    )
    
    configuration = models.JSONField(
        default=dict,
        help_text=_('Channel configuration (JSON)')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this channel is currently active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('notification channel')
        verbose_name_plural = _('notification channels')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class NotificationTemplate(models.Model):
    """
    Templates for notifications with variables that can be substituted.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Template name')
    )
    
    subject = models.CharField(
        max_length=255,
        help_text=_('Subject template with variables')
    )
    
    content = models.TextField(
        help_text=_('Content template with variables')
    )
    
    html_content = models.TextField(
        blank=True,
        help_text=_('HTML content template (for email)')
    )
    
    variables = models.JSONField(
        default=list,
        help_text=_('List of variables used in this template')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('notification template')
        verbose_name_plural = _('notification templates')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """
    Represents a notification sent to a user.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SENT = 'SENT', _('Sent')
        DELIVERED = 'DELIVERED', _('Delivered')
        READ = 'READ', _('Read')
        FAILED = 'FAILED', _('Failed')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text=_('User who will receive the notification')
    )
    
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.PROTECT,
        related_name='notifications',
        help_text=_('Template used for this notification')
    )
    
    channel = models.ForeignKey(
        NotificationChannel,
        on_delete=models.PROTECT,
        related_name='notifications',
        help_text=_('Channel used to send this notification')
    )
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_('Current status of the notification')
    )
    
    subject = models.CharField(
        max_length=255,
        help_text=_('Final subject after variable substitution')
    )
    
    content = models.TextField(
        help_text=_('Final content after variable substitution')
    )
    
    data = models.JSONField(
        default=dict,
        help_text=_('Data used for variable substitution')
    )
    
    error_message = models.TextField(
        blank=True,
        help_text=_('Error message if sending failed')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user} - {self.subject} ({self.status})" 