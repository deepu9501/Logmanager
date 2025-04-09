"""
API views for the logs app.
"""

from django.db.models import Count, Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
import csv
from datetime import datetime
from django.core.paginator import Paginator
from classification.tasks import classify_log
from users.permissions import IsAdminOrManager, IsAdmin
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import LogSource, LogEntry
from .serializers import (
    LogSourceSerializer,
    LogEntrySerializer,
    LogEntryListSerializer,
    LogEntryCreateSerializer,
    LogEntryBulkCreateSerializer,
    LogEntryUpdateSerializer
)
from .filters import LogEntryFilter
from django.contrib import messages
from django.urls import reverse

# HTML Template Views
class LogListView(LoginRequiredMixin, ListView):
    model = LogEntry
    template_name = 'logs/log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = LogEntry.objects.all().select_related('source')
        
        # Apply filters
        self.filterset = LogEntryFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.order_by('-timestamp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['total_logs'] = LogEntry.objects.count()
        context['error_logs'] = LogEntry.objects.filter(severity='ERROR').count()
        context['warning_logs'] = LogEntry.objects.filter(severity='WARNING').count()
        context['info_logs'] = LogEntry.objects.filter(severity='INFO').count()
        context['sources'] = LogSource.objects.all()
        context['severity_choices'] = LogEntry.SEVERITY_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        """Handle bulk actions"""
        action = request.POST.get('action')
        log_ids = request.POST.getlist('log_ids')
        
        if action == 'mark_read':
            LogEntry.objects.filter(id__in=log_ids).update(is_read=True)
            messages.success(request, f'Marked {len(log_ids)} logs as read')
        elif action == 'mark_unread':
            LogEntry.objects.filter(id__in=log_ids).update(is_read=False)
            messages.success(request, f'Marked {len(log_ids)} logs as unread')
        elif action == 'flag':
            LogEntry.objects.filter(id__in=log_ids).update(is_flagged=True)
            messages.success(request, f'Flagged {len(log_ids)} logs')
        elif action == 'unflag':
            LogEntry.objects.filter(id__in=log_ids).update(is_flagged=False)
            messages.success(request, f'Unflagged {len(log_ids)} logs')
        elif action == 'delete':
            LogEntry.objects.filter(id__in=log_ids).delete()
            messages.success(request, f'Deleted {len(log_ids)} logs')
        
        return HttpResponseRedirect(reverse('logs:log_list'))

class LogCreateView(LoginRequiredMixin, CreateView):
    model = LogEntry
    template_name = 'logs/log_form.html'
    fields = ['source', 'severity', 'message']
    success_url = reverse_lazy('logs:log_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class LogDetailView(LoginRequiredMixin, DetailView):
    model = LogEntry
    template_name = 'logs/log_detail.html'
    context_object_name = 'log'

class LogUpdateView(LoginRequiredMixin, UpdateView):
    model = LogEntry
    template_name = 'logs/log_form.html'
    fields = ['source', 'severity', 'message']
    success_url = reverse_lazy('logs:log_list')

class LogDeleteView(LoginRequiredMixin, DeleteView):
    model = LogEntry
    template_name = 'logs/log_confirm_delete.html'
    success_url = reverse_lazy('logs:log_list')

# Log Sources UI Views
class LogSourceListView(LoginRequiredMixin, ListView):
    model = LogSource
    template_name = 'logs/log_sources.html'
    context_object_name = 'sources'
    
    def get_queryset(self):
        queryset = LogSource.objects.annotate(log_count=Count('log_entries'))
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add source type statistics
        source_types = list(LogSource.objects.values('type').annotate(count=Count('id')))
        context['source_types'] = source_types
        
        # Add JSON serialized data for charts
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        
        # Prepare data for charts in JSON format
        context['source_types_json'] = json.dumps(source_types, cls=DjangoJSONEncoder)
        
        # Get sources with log counts
        sources_with_logs = list(LogSource.objects.values('name').annotate(
            log_count=Count('log_entries')
        ).order_by('-log_count')[:5])  # Top 5 sources by log count
        
        context['sources_with_logs_json'] = json.dumps(sources_with_logs, cls=DjangoJSONEncoder)
        
        return context

class LogSourceCreateView(LoginRequiredMixin, CreateView):
    model = LogSource
    template_name = 'logs/log_source_form.html'
    fields = ['name', 'type', 'description', 'is_active']
    success_url = reverse_lazy('logs:source_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Log source "{form.instance.name}" created successfully!')
        return super().form_valid(form)

class LogSourceUpdateView(LoginRequiredMixin, UpdateView):
    model = LogSource
    template_name = 'logs/log_source_form.html'
    fields = ['name', 'type', 'description', 'is_active']
    success_url = reverse_lazy('logs:source_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Log source "{form.instance.name}" updated successfully!')
        return super().form_valid(form)

class LogSourceDeleteView(LoginRequiredMixin, DeleteView):
    model = LogSource
    template_name = 'logs/log_confirm_delete.html'
    success_url = reverse_lazy('logs:source_list')
    context_object_name = 'source'
    
    def delete(self, request, *args, **kwargs):
        source = self.get_object()
        messages.success(request, f'Log source "{source.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

def export_log_sources(request):
    """
    Export log sources to CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="log_sources.csv"'
    
    sources = LogSource.objects.annotate(log_count=Count('log_entries'))
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Type', 'Description', 'Status', 'Log Count', 'Created', 'Last Updated'])
    
    for source in sources:
        writer.writerow([
            source.name,
            source.type,
            source.description,
            'Active' if source.is_active else 'Inactive',
            source.log_count,
            source.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            source.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

# API Views
class LogSourceViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing log sources.
    """
    queryset = LogSource.objects.annotate(log_count=Count('log_entries'))
    serializer_class = LogSourceSerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'type']
    ordering_fields = ['name', 'type', 'created_at', 'log_count']
    ordering = ['name']
    
    def get_permissions(self):
        """
        Restrict create, update, partial_update and destroy actions to admin users.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdmin]
        return super().get_permissions()


class LogEntryViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing log entries.
    """
    queryset = LogEntry.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LogEntryFilter
    search_fields = ['message', 'user_id', 'ip_address']
    ordering_fields = ['timestamp', 'severity', 'source', 'created_at']
    ordering = ['-timestamp']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action.
        """
        if self.action == 'create':
            return LogEntryCreateSerializer
        elif self.action == 'list':
            return LogEntryListSerializer
        elif self.action in ['update', 'partial_update']:
            return LogEntryUpdateSerializer
        elif self.action == 'bulk_create':
            return LogEntryBulkCreateSerializer
        return LogEntrySerializer
    
    def get_permissions(self):
        """
        Set permissions based on the action.
        """
        if self.action in ['create', 'bulk_create']:
            # Allow any authenticated user to create logs
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only admin or manager can update or delete logs
            self.permission_classes = [IsAdminOrManager]
        else:
            # Any authenticated user can view logs
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """
        Create a log entry and trigger classification.
        """
        log_entry = serializer.save()
        classify_log.delay(log_entry.id)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple log entries at once.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logs = serializer.save()
        
        # Trigger classification for each log
        for log in logs:
            classify_log.delay(log.id)
        
        return Response(
            {'message': f'Successfully created {len(logs)} log entries.'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a log entry as read.
        """
        log_entry = self.get_object()
        log_entry.is_read = True
        log_entry.save(update_fields=['is_read'])
        return Response({'status': 'log marked as read'})
    
    @action(detail=True, methods=['patch'])
    def flag(self, request, pk=None):
        """
        Flag or unflag a log entry.
        """
        log_entry = self.get_object()
        log_entry.is_flagged = not log_entry.is_flagged
        log_entry.save(update_fields=['is_flagged'])
        status_msg = 'flagged' if log_entry.is_flagged else 'unflagged'
        return Response({'status': f'log {status_msg}'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all filtered log entries as read.
        """
        filtered_queryset = self.filter_queryset(self.get_queryset())
        count = filtered_queryset.update(is_read=True)
        return Response({'status': f'marked {count} logs as read'})

class LogEntryListView(LoginRequiredMixin, ListView):
    model = LogEntry
    template_name = 'logs/log_entry_list.html'
    context_object_name = 'log_entries'
    paginate_by = 50

    def get_queryset(self):
        queryset = LogEntry.objects.all().select_related('source')
        
        # Apply filters
        self.filterset = LogEntryFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['total_logs'] = LogEntry.objects.count()
        context['error_logs'] = LogEntry.objects.filter(severity='ERROR').count()
        context['warning_logs'] = LogEntry.objects.filter(severity='WARNING').count()
        context['info_logs'] = LogEntry.objects.filter(severity='INFO').count()
        context['sources'] = LogSource.objects.all()
        return context

class LogEntryDetailView(LoginRequiredMixin, DetailView):
    model = LogEntry
    template_name = 'logs/log_entry_detail.html'
    context_object_name = 'log_entry'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_logs'] = LogEntry.objects.filter(
            source=self.object.source,
            severity=self.object.severity
        ).exclude(id=self.object.id)[:5]
        return context

def log_export(request):
    """Export logs to CSV file"""
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)
    
    # Get filtered queryset
    filter_set = LogEntryFilter(request.GET, queryset=LogEntry.objects.all())
    queryset = filter_set.qs
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Source', 'Severity', 'Category', 'Event ID', 'Message'])
    
    for log in queryset:
        writer.writerow([
            log.timestamp,
            log.source.name,
            log.severity,
            log.category,
            log.event_id,
            log.message
        ])
    
    return response

def log_stats(request):
    """API endpoint for log statistics"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    stats = {
        'total_logs': LogEntry.objects.count(),
        'error_logs': LogEntry.objects.filter(severity='ERROR').count(),
        'warning_logs': LogEntry.objects.filter(severity='WARNING').count(),
        'info_logs': LogEntry.objects.filter(severity='INFO').count(),
        'logs_by_source': list(LogEntry.objects.values('source__name').annotate(count=Count('id'))),
        'logs_by_severity': list(LogEntry.objects.values('severity').annotate(count=Count('id'))),
        'logs_by_hour': list(LogEntry.objects.annotate(hour=datetime.now().hour).values('hour').annotate(count=Count('id'))),
    }
    return JsonResponse(stats)

def search_logs(request):
    """API endpoint for log search"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Search query required'}, status=400)
    
    logs = LogEntry.objects.filter(
        Q(message__icontains=query) |
        Q(source__name__icontains=query) |
        Q(severity__icontains=query)
    ).select_related('source')[:100]
    
    results = [{
        'id': log.id,
        'message': log.message,
        'source': log.source.name,
        'severity': log.severity,
        'timestamp': log.timestamp.isoformat(),
        'url': reverse('logs:log_entry_detail', kwargs={'pk': log.id})
    } for log in logs]
    
    return JsonResponse({'results': results})