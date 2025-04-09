"""
User models for the log management system.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model for the log management system with role-based access control.
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        MANAGER = 'MANAGER', _('Manager')
        ANALYST = 'ANALYST', _('Analyst')
        VIEWER = 'VIEWER', _('Viewer')
        AUDITOR = 'AUDITOR', _('Auditor')
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text=_('User role determines permission level')
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Department or organization unit')
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        help_text=_('Contact phone number')
    )
    
    notification_email = models.BooleanField(
        default=True,
        help_text=_('Receive email notifications')
    )
    
    notification_sms = models.BooleanField(
        default=False,
        help_text=_('Receive SMS notifications')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER
        
    @property
    def is_analyst(self):
        return self.role == self.Role.ANALYST
    
    @property
    def is_auditor(self):
        return self.role == self.Role.AUDITOR


class UserActivity(models.Model):
    """
    Tracks user activity in the system for auditing purposes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_('IP address of the user')
    )
    
    action = models.CharField(
        max_length=255,
        help_text=_('Action performed by the user')
    )
    
    object_type = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Type of object affected')
    )
    
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_('ID of the affected object')
    )
    
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Additional details about the activity')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}" 