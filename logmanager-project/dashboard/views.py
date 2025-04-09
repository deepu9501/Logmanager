"""
API views for the dashboard app.
"""

# import pandas as pd
from datetime import timedelta
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from .models import Dashboard, Widget, SavedQuery
from .serializers import (
    DashboardSerializer,
    WidgetSerializer,
    SavedQuerySerializer
)
from logs.models import LogEntry, LogSource
from classification.models import LogClassification
from users.permissions import IsOwnerOrAdmin
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class DashboardViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing dashboards.
    """
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return dashboards owned by the current user.
        """
        return Dashboard.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Set the user when creating a dashboard.
        """
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Set this dashboard as the default for the user.
        """
        dashboard = self.get_object()
        
        # Remove default status from all dashboards for this user
        Dashboard.objects.filter(user=request.user).update(is_default=False)
        
        # Set this dashboard as default
        dashboard.is_default = True
        dashboard.save(update_fields=['is_default'])
        
        return Response({'status': f'Dashboard "{dashboard.name}" set as default'})


class WidgetViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing dashboard widgets.
    """
    serializer_class = WidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return widgets for dashboards owned by the current user.
        """
        dashboard_id = self.request.query_params.get('dashboard', None)
        queryset = Widget.objects.filter(dashboard__user=self.request.user)
        
        if dashboard_id:
            queryset = queryset.filter(dashboard_id=dashboard_id)
            
        return queryset


class SavedQueryViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing saved log queries.
    """
    serializer_class = SavedQuerySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return saved queries owned by the current user or marked as public.
        """
        user = self.request.user
        return SavedQuery.objects.filter(
            Q(user=user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        """
        Set the user when creating a saved query.
        """
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def statistics_view(request):
    """
    General statistics for the dashboard.
    """
    # Time ranges
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Log counts by period
    total_logs = LogEntry.objects.count()
    logs_today = LogEntry.objects.filter(timestamp__gte=today).count()
    logs_yesterday = LogEntry.objects.filter(timestamp__gte=yesterday, timestamp__lt=today).count()
    logs_this_week = LogEntry.objects.filter(timestamp__gte=week_ago).count()
    logs_this_month = LogEntry.objects.filter(timestamp__gte=month_ago).count()
    
    # Log counts by severity
    severity_counts = dict(LogEntry.objects.values('severity').annotate(count=Count('id')).values_list('severity', 'count'))
    
    # Critical logs trend (last 7 days)
    critical_logs_trend = []
    for i in range(7):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = LogEntry.objects.filter(
            severity='CRITICAL',
            timestamp__gte=day,
            timestamp__lt=next_day
        ).count()
        critical_logs_trend.append({
            'date': day.date().isoformat(),
            'count': count
        })
    
    # Top log sources
    top_sources = LogSource.objects.annotate(
        log_count=Count('log_entries')
    ).values('id', 'name', 'log_count').order_by('-log_count')[:5]
    
    # Top classifications
    top_classifications = LogClassification.objects.annotate(
        log_count=Count('log_entries')
    ).values('id', 'name', 'log_count').order_by('-log_count')[:5]
    
    return Response({
        'log_counts': {
            'total': total_logs,
            'today': logs_today,
            'yesterday': logs_yesterday,
            'this_week': logs_this_week,
            'this_month': logs_this_month
        },
        'severity_counts': severity_counts,
        'critical_logs_trend': critical_logs_trend,
        'top_sources': top_sources,
        'top_classifications': top_classifications
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def widget_data_view(request, widget_type):
    """
    Retrieve data for a specific widget type.
    """
    # Common query parameters
    days = int(request.query_params.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    if widget_type == Widget.WidgetType.LOGS_COUNT:
        # Logs count over time
        logs_by_day = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            next_day = day + timedelta(days=1)
            count = LogEntry.objects.filter(
                timestamp__gte=day,
                timestamp__lt=next_day
            ).count()
            logs_by_day.append({
                'date': day.date().isoformat(),
                'count': count
            })
        return Response(logs_by_day)
    
    elif widget_type == Widget.WidgetType.SEVERITY_DISTRIBUTION:
        # Logs by severity
        severity_counts = list(LogEntry.objects.filter(
            timestamp__gte=start_date
        ).values('severity').annotate(count=Count('id')).order_by('severity'))
        return Response(severity_counts)
    
    elif widget_type == Widget.WidgetType.RECENT_LOGS:
        # Most recent logs
        limit = int(request.query_params.get('limit', 10))
        logs = LogEntry.objects.filter(
            timestamp__gte=start_date
        ).order_by('-timestamp')[:limit].values(
            'id', 'source__name', 'severity', 'message', 'timestamp'
        )
        return Response(list(logs))
    
    elif widget_type == Widget.WidgetType.CLASSIFICATION_DISTRIBUTION:
        # Logs by classification
        class_counts = list(LogEntry.objects.filter(
            timestamp__gte=start_date,
            classification__isnull=False
        ).values('classification__name').annotate(count=Count('id')).order_by('-count'))
        # Add unclassified count
        unclassified_count = LogEntry.objects.filter(
            timestamp__gte=start_date,
            classification__isnull=True
        ).count()
        class_counts.append({'classification__name': 'Unclassified', 'count': unclassified_count})
        return Response(class_counts)
    
    elif widget_type == Widget.WidgetType.TOP_SOURCES:
        # Top log sources
        sources = list(LogSource.objects.annotate(
            log_count=Count('log_entries', filter=Q(log_entries__timestamp__gte=start_date))
        ).values('name', 'log_count').order_by('-log_count')[:10])
        return Response(sources)
    
    elif widget_type == Widget.WidgetType.SYSTEM_STATUS:
        # Overall system status
        critical_count = LogEntry.objects.filter(
            severity='CRITICAL',
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        error_count = LogEntry.objects.filter(
            severity='ERROR',
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Determine status based on log levels
        status = 'healthy'
        if critical_count > 0:
            status = 'critical'
        elif error_count > 5:
            status = 'warning'
        
        return Response({
            'status': status,
            'critical_count_24h': critical_count,
            'error_count_24h': error_count,
            'sources_count': LogSource.objects.count(),
            'last_updated': timezone.now().isoformat()
        })
    
    # Unsupported widget type
    return Response(
        {'error': f'Unsupported widget type: {widget_type}'},
        status=status.HTTP_400_BAD_REQUEST
    )


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard view that displays system statistics and recent logs.
    Requires user to be logged in.
    """
    template_name = 'dashboard/index.html'
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics data to context
        # These would normally come from database queries
        context['total_logs'] = 256
        context['error_count'] = 24
        context['warning_count'] = 38
        context['info_count'] = 194
        context['notification_count'] = 12
        context['source_count'] = 5
        
        # Add some sample recent logs
        # In a real app, these would come from the database
        context['recent_logs'] = [
            {
                'id': 1,
                'timestamp': '2024-03-26 12:34:56',
                'source': {'name': 'Web Server'},
                'level': 'INFO',
                'message': 'Server restarted successfully'
            },
            {
                'id': 2,
                'timestamp': '2024-03-26 11:23:45',
                'source': {'name': 'Database'},
                'level': 'WARNING',
                'message': 'Database connection pool reaching capacity (85%)'
            },
            {
                'id': 3,
                'timestamp': '2024-03-26 10:12:34',
                'source': {'name': 'API Gateway'},
                'level': 'ERROR',
                'message': 'Authentication service timeout after 30s'
            }
        ]
        
        return context 


def auth_test_view(request):
    """View for testing API authentication"""
    from django.shortcuts import render
    return render(request, 'dashboard/auth_test.html')