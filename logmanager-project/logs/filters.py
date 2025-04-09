"""
Filters for the logs app.
"""

import django_filters
from django.db.models import Q
from django_filters import FilterSet, CharFilter, ChoiceFilter, DateFilter, ModelChoiceFilter
from .models import LogEntry, LogSource


class LogEntryFilter(FilterSet):
    """
    Filter for LogEntry model.
    """
    search = CharFilter(method='search_filter', label='Search')
    severity = ChoiceFilter(choices=LogEntry.SEVERITY_CHOICES, label='Severity')
    source = ModelChoiceFilter(queryset=LogSource.objects.all(), field_name='source', label='Source')
    date_from = DateFilter(field_name='timestamp', lookup_expr='gte', label='Date From')
    date_to = DateFilter(field_name='timestamp', lookup_expr='lte', label='Date To')
    category = CharFilter(field_name='category', lookup_expr='icontains', label='Category')
    event_id = CharFilter(field_name='event_id', lookup_expr='icontains', label='Event ID')
    is_read = ChoiceFilter(
        choices=[('True', 'Read'), ('False', 'Unread')],
        label='Status'
    )
    is_flagged = ChoiceFilter(
        choices=[('True', 'Flagged'), ('False', 'Not Flagged')],
        label='Flag Status'
    )

    class Meta:
        model = LogEntry
        fields = ['severity', 'source', 'date_from', 'date_to', 'category', 'event_id', 'is_read', 'is_flagged']

    def search_filter(self, queryset, name, value):
        """
        Search in message, source name, severity, category, and event ID fields.
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(message__icontains=value) |
            Q(source__name__icontains=value) |
            Q(severity__icontains=value) |
            Q(category__icontains=value) |
            Q(event_id__icontains=value)
        ) 