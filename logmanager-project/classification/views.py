"""
API views for the classification app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import LogClassification, ClassificationKeyword, ClassificationModel
from .serializers import (
    LogClassificationSerializer,
    ClassificationKeywordSerializer,
    ClassificationModelSerializer
)
from .tasks import train_classification_model, classify_log
from users.permissions import IsAdminOrManager, IsAdmin


class LogClassificationViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing log classifications.
    """
    queryset = LogClassification.objects.all()
    serializer_class = LogClassificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Restrict create, update, partial_update and destroy actions to admin or manager users.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrManager]
        return super().get_permissions()


class ClassificationKeywordViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing classification keywords.
    """
    queryset = ClassificationKeyword.objects.all()
    serializer_class = ClassificationKeywordSerializer
    permission_classes = [IsAdminOrManager]
    filterset_fields = ['classification']


class ClassificationModelViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing classification models.
    """
    queryset = ClassificationModel.objects.all()
    serializer_class = ClassificationModelSerializer
    permission_classes = [IsAdmin]
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate this model and deactivate all others.
        """
        model = self.get_object()
        
        # Deactivate all models
        ClassificationModel.objects.all().update(is_active=False)
        
        # Activate the selected model
        model.is_active = True
        model.save()
        
        return Response({'status': f'Model {model.name} v{model.version} activated'})


@api_view(['POST'])
@permission_classes([IsAdmin])
def train_model_view(request):
    """
    Trigger training of a new classification model.
    """
    # Schedule the Celery task
    task = train_classification_model.delay()
    
    return Response({
        'status': 'Classification model training started',
        'task_id': task.id
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def classify_log_view(request, log_id):
    """
    Manually trigger classification for a specific log entry.
    """
    # Schedule the Celery task
    task = classify_log.delay(log_id)
    
    return Response({
        'status': f'Classification of log {log_id} initiated',
        'task_id': task.id
    }) 