"""
URL patterns for the logs app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'logs'

router = DefaultRouter()
router.register('sources', views.LogSourceViewSet, basename='source')
router.register('entries', views.LogEntryViewSet, basename='entry')

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    path('api/stats/', views.log_stats, name='log_stats'),
    path('api/search/', views.search_logs, name='log_search'),
    
    # HTML Template URLs
    path('', views.LogListView.as_view(), name='log_list'),
    path('add/', views.LogCreateView.as_view(), name='log_add'),
    path('<int:pk>/', views.LogDetailView.as_view(), name='log_detail'),
    path('<int:pk>/edit/', views.LogUpdateView.as_view(), name='log_edit'),
    path('<int:pk>/delete/', views.LogDeleteView.as_view(), name='log_delete'),
    path('export/', views.log_export, name='log_export'),
    
    # Log Source Management URLs
    path('sources/', views.LogSourceListView.as_view(), name='source_list'),
    path('sources/add/', views.LogSourceCreateView.as_view(), name='create_source'),
    path('sources/<int:pk>/edit/', views.LogSourceUpdateView.as_view(), name='update_source'),
    path('sources/<int:pk>/delete/', views.LogSourceDeleteView.as_view(), name='delete_source'),
    path('sources/export/', views.export_log_sources, name='export_sources'),
] 