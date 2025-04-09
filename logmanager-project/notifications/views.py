"""
API views for the notifications app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import NotificationChannel, NotificationTemplate, Notification
from .serializers import (
    NotificationChannelSerializer,
    NotificationTemplateSerializer,
    NotificationSerializer,
    NotificationCreateSerializer
)
from .tasks import send_notification
from users.permissions import IsAdminOrManager, IsAdmin
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


class NotificationChannelViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing notification channels.
    """
    queryset = NotificationChannel.objects.all()
    serializer_class = NotificationChannelSerializer
    permission_classes = [IsAdmin]


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing notification templates.
    """
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAdminOrManager]


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter notifications to show only those for the current user.
        Admins and managers can see all notifications if 'all' query param is provided.
        """
        user = self.request.user
        
        # Check if admin/manager is requesting all notifications
        show_all = (
            self.request.query_params.get('all', '').lower() == 'true' and
            (user.is_admin or user.is_manager)
        )
        
        if show_all:
            return Notification.objects.all()
        return Notification.objects.filter(user=user)
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'create':
            return NotificationCreateSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        List unread notifications for the current user.
        """
        unread = self.get_queryset().filter(
            status__in=[Notification.Status.SENT, Notification.Status.DELIVERED]
        )
        page = self.paginate_queryset(unread)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unread, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """
        Resend a notification.
        """
        notification = self.get_object()
        
        # Only failed notifications can be resent
        if notification.status != Notification.Status.FAILED:
            return Response(
                {'error': 'Only failed notifications can be resent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset status to PENDING
        notification.status = Notification.Status.PENDING
        notification.error_message = ''
        notification.save(update_fields=['status', 'error_message', 'updated_at'])
        
        # Resend based on channel type
        if notification.channel.type == NotificationChannel.ChannelType.EMAIL:
            from .tasks import send_email_notification
            send_email_notification.delay(notification.id)
        elif notification.channel.type == NotificationChannel.ChannelType.WEBSOCKET:
            from .tasks import send_websocket_notification
            send_websocket_notification.delay(notification.id)
        
        return Response({'status': 'Notification resend initiated'})


# HTML Template Views
class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        status = self.request.GET.get('status', 'all')
        
        if status == 'unread':
            queryset = queryset.filter(status__in=[Notification.Status.SENT, Notification.Status.DELIVERED])
        elif status == 'read':
            queryset = queryset.filter(status=Notification.Status.READ)
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            user=self.request.user,
            status__in=[Notification.Status.SENT, Notification.Status.DELIVERED]
        ).count()
        return context

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_as_read(request, pk):
    """
    Mark a notification as read.
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    if notification.status != Notification.Status.READ:
        notification.status = Notification.Status.READ
        notification.read_at = timezone.now()
        notification.save(update_fields=['status', 'read_at', 'updated_at'])
    
    return JsonResponse({'status': 'success'})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_as_read(request):
    """
    Mark all unread notifications for the current user as read.
    """
    count = Notification.objects.filter(
        user=request.user,
        status__in=[Notification.Status.SENT, Notification.Status.DELIVERED]
    ).update(
        status=Notification.Status.READ,
        read_at=timezone.now()
    )
    
    return JsonResponse({'status': 'success'}) 