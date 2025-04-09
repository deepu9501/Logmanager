"""
URL patterns for the dashboard app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAuthenticated
from . import views

app_name = 'dashboard'

# API router configuration
router = DefaultRouter()
router.register('dashboards', views.DashboardViewSet, basename='dashboard')
router.register('widgets', views.WidgetViewSet, basename='widget')
router.register('saved-queries', views.SavedQueryViewSet, basename='saved-query')

urlpatterns = [
    # Dashboard web view (HTML)
    path('', views.DashboardView.as_view(), name='index'),
    
    # API endpoints with authentication
    path('api/', include(router.urls)),
    
    # Other HTML views and endpoints
    path('statistics/', views.statistics_view, name='statistics'),
    path('widget-data/<str:widget_type>/', views.widget_data_view, name='widget-data'),
    path('auth-test/', views.auth_test_view, name='auth-test'),
]