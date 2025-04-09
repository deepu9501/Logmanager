"""
Models for the classification app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class LogClassification(models.Model):
    """
    Represents a classification category for log entries.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Classification name')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Description of this classification')
    )
    
    priority = models.PositiveSmallIntegerField(
        default=0,
        help_text=_('Priority level (higher number = higher priority)')
    )
    
    color_code = models.CharField(
        max_length=7,
        default='#CCCCCC',
        help_text=_('Color code for UI display (hex format)')
    )
    
    notification_enabled = models.BooleanField(
        default=False,
        help_text=_('Whether to send notifications for logs with this classification')
    )
    
    pattern = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Regex pattern for automatic classification')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('log classification')
        verbose_name_plural = _('log classifications')
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return self.name


class ClassificationKeyword(models.Model):
    """
    Keywords associated with classification categories for ML-based classification.
    """
    classification = models.ForeignKey(
        LogClassification,
        on_delete=models.CASCADE,
        related_name='keywords',
        help_text=_('The classification this keyword belongs to')
    )
    
    keyword = models.CharField(
        max_length=100,
        help_text=_('Keyword used for classification')
    )
    
    weight = models.FloatField(
        default=1.0,
        help_text=_('Weight of this keyword (higher = more important)')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('classification keyword')
        verbose_name_plural = _('classification keywords')
        unique_together = ['classification', 'keyword']
        ordering = ['-weight']
    
    def __str__(self):
        return f"{self.keyword} ({self.classification})"


class ClassificationModel(models.Model):
    """
    Represents a trained machine learning model for log classification.
    """
    name = models.CharField(
        max_length=100,
        help_text=_('Model name')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Description of this model')
    )
    
    version = models.CharField(
        max_length=20,
        help_text=_('Model version')
    )
    
    model_file = models.FileField(
        upload_to='classification_models/',
        help_text=_('Trained model file')
    )
    
    vectorizer_file = models.FileField(
        upload_to='classification_models/',
        help_text=_('Text vectorizer file')
    )
    
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Model accuracy score')
    )
    
    is_active = models.BooleanField(
        default=False,
        help_text=_('Whether this model is currently active')
    )
    
    trained_at = models.DateTimeField(
        help_text=_('When the model was trained')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('classification model')
        verbose_name_plural = _('classification models')
        ordering = ['-created_at']
        unique_together = ['name', 'version']
    
    def __str__(self):
        return f"{self.name} v{self.version}" 