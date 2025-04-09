"""
URL patterns for the notifications app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'web_notifications'

router = DefaultRouter()
router.register('templates', views.NotificationTemplateViewSet, basename='template')
router.register('channels', views.NotificationChannelViewSet, basename='channel')
router.register('', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # HTML Template URLs
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('mark-as-read/<int:pk>/', views.mark_notification_as_read, name='mark-as-read'),
    path('mark-all-as-read/', views.mark_all_notifications_as_read, name='mark-all-as-read'),
]