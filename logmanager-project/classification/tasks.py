"""
Celery tasks for automatic log classification.
"""

import re
import logging
from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from notifications.tasks import send_notification

logger = logging.getLogger(__name__)


@shared_task
def classify_log(log_entry_id):
    """
    Classify a log entry based on regex patterns and ML model.
    
    This task:
    1. Attempts to classify the log using regex patterns
    2. If no match, uses ML-based classification
    3. Updates the log entry with the classification
    4. Triggers notifications if needed
    """
    try:
        # Importing here to avoid circular imports
        from logs.models import LogEntry
        from classification.models import LogClassification
        from classification.utils import classify_with_ml_model
        
        # Get the log entry
        log_entry = LogEntry.objects.get(id=log_entry_id)
        
        # Skip if already classified
        if log_entry.classification is not None:
            return f"Log entry {log_entry_id} is already classified"
        
        # Try pattern-based classification first
        classifications_with_patterns = LogClassification.objects.exclude(
            Q(pattern__isnull=True) | Q(pattern='')
        )
        
        for classification in classifications_with_patterns:
            try:
                if re.search(classification.pattern, log_entry.message, re.IGNORECASE):
                    log_entry.classification = classification
                    log_entry.save(update_fields=['classification', 'updated_at'])
                    
                    # Check if notification is needed
                    if classification.notification_enabled and (
                        log_entry.severity in ['ERROR', 'CRITICAL']
                    ):
                        send_notification.delay(
                            'log_classified',
                            log_entry_id=log_entry.id,
                            classification_id=classification.id
                        )
                    
                    return f"Log entry {log_entry_id} classified as {classification.name} using regex pattern"
            except re.error:
                logger.error(f"Invalid regex pattern in classification {classification.id}: {classification.pattern}")
                continue
        
        # Try ML-based classification if no pattern match
        classification = classify_with_ml_model(log_entry.message)
        if classification:
            log_entry.classification = classification
            log_entry.save(update_fields=['classification', 'updated_at'])
            
            # Check if notification is needed
            if classification.notification_enabled and (
                log_entry.severity in ['ERROR', 'CRITICAL']
            ):
                send_notification.delay(
                    'log_classified',
                    log_entry_id=log_entry.id,
                    classification_id=classification.id
                )
            
            return f"Log entry {log_entry_id} classified as {classification.name} using ML model"
        
        # No classification found
        return f"Could not classify log entry {log_entry_id}"
    
    except LogEntry.DoesNotExist:
        logger.error(f"Log entry {log_entry_id} not found")
        return f"Log entry {log_entry_id} not found"
    except Exception as e:
        logger.error(f"Error classifying log entry {log_entry_id}: {str(e)}")
        return f"Error classifying log entry {log_entry_id}: {str(e)}"


@shared_task
def train_classification_model():
    """
    Train a new ML model for log classification.
    
    This task:
    1. Retrieves classified logs from database
    2. Extracts features and trains a new model
    3. Saves the model for future use
    4. Updates the active model
    """
    try:
        from classification.utils import train_model
        
        # Call the training function from utils
        model_id = train_model()
        
        if model_id:
            return f"Successfully trained and saved model {model_id}"
        return "Failed to train model"
    
    except Exception as e:
        logger.error(f"Error training classification model: {str(e)}")
        return f"Error training classification model: {str(e)}"


@shared_task
def reclassify_all_logs():
    """
    Reclassify all unclassified logs in the system.
    
    This is useful after training a new model or adding new classification patterns.
    """
    try:
        from logs.models import LogEntry
        
        # Get all unclassified logs
        unclassified_logs = LogEntry.objects.filter(classification__isnull=True)
        count = unclassified_logs.count()
        
        # Schedule classification for each log
        for log_entry in unclassified_logs:
            classify_log.delay(log_entry.id)
        
        return f"Scheduled reclassification of {count} logs"
    
    except Exception as e:
        logger.error(f"Error scheduling reclassification: {str(e)}")
        return f"Error scheduling reclassification: {str(e)}" 