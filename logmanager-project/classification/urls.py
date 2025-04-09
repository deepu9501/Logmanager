"""
URL patterns for the classification app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'classification'

router = DefaultRouter()
router.register('classifications', views.LogClassificationViewSet, basename='classification')
router.register('keywords', views.ClassificationKeywordViewSet, basename='keyword')
router.register('models', views.ClassificationModelViewSet, basename='model')

urlpatterns = [
    path('', include(router.urls)),
    path('train-model/', views.train_model_view, name='train-model'),
    path('classify-log/<int:log_id>/', views.classify_log_view, name='classify-log'),
] 