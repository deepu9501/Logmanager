"""
Models for the dashboard app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Dashboard(models.Model):
    """
    Represents a customizable dashboard for users.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboards',
        help_text=_('User who owns this dashboard')
    )
    
    name = models.CharField(
        max_length=100,
        help_text=_('Dashboard name')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Dashboard description')
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text=_('Whether this is the default dashboard for the user')
    )
    
    layout = models.JSONField(
        default=dict,
        help_text=_('Dashboard layout configuration')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboards')
        ordering = ['-is_default', 'name']
        unique_together = [['user', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Widget(models.Model):
    """
    Represents a widget that can be placed on a dashboard.
    """
    class WidgetType(models.TextChoices):
        LOGS_COUNT = 'LOGS_COUNT', _('Logs Count')
        SEVERITY_DISTRIBUTION = 'SEVERITY_DISTRIBUTION', _('Severity Distribution')
        RECENT_LOGS = 'RECENT_LOGS', _('Recent Logs')
        CLASSIFICATION_DISTRIBUTION = 'CLASSIFICATION_DISTRIBUTION', _('Classification Distribution')
        TIME_SERIES = 'TIME_SERIES', _('Time Series')
        TOP_SOURCES = 'TOP_SOURCES', _('Top Sources')
        SYSTEM_STATUS = 'SYSTEM_STATUS', _('System Status')
        CUSTOM_CHART = 'CUSTOM_CHART', _('Custom Chart')
    
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets',
        help_text=_('Dashboard this widget belongs to')
    )
    
    type = models.CharField(
        max_length=30,
        choices=WidgetType.choices,
        help_text=_('Type of widget')
    )
    
    title = models.CharField(
        max_length=100,
        help_text=_('Widget title')
    )
    
    configuration = models.JSONField(
        default=dict,
        help_text=_('Widget configuration')
    )
    
    position_x = models.PositiveSmallIntegerField(
        default=0,
        help_text=_('Horizontal position (grid column)')
    )
    
    position_y = models.PositiveSmallIntegerField(
        default=0,
        help_text=_('Vertical position (grid row)')
    )
    
    width = models.PositiveSmallIntegerField(
        default=1,
        help_text=_('Width in grid units')
    )
    
    height = models.PositiveSmallIntegerField(
        default=1,
        help_text=_('Height in grid units')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('widget')
        verbose_name_plural = _('widgets')
        ordering = ['dashboard', 'position_y', 'position_x']
    
    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"


class SavedQuery(models.Model):
    """
    Represents a saved search query for logs.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_queries',
        help_text=_('User who created this saved query')
    )
    
    name = models.CharField(
        max_length=100,
        help_text=_('Query name')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Query description')
    )
    
    query_params = models.JSONField(
        help_text=_('Query parameters')
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text=_('Whether this query is visible to other users')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('saved query')
        verbose_name_plural = _('saved queries')
        ordering = ['name']
        unique_together = [['user', 'name']]
    
    def __str__(self):
        return self.name 