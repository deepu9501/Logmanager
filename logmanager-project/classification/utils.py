"""
Utility functions for log classification.
"""

import os
import pickle
import logging
import numpy as np
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

logger = logging.getLogger(__name__)


def classify_with_ml_model(log_message):
    """
    Classify a log message using the active ML model.
    
    Args:
        log_message (str): The log message to classify
        
    Returns:
        LogClassification: The classification object or None if classification fails
    """
    try:
        from .models import ClassificationModel, LogClassification
        
        # Get the active model
        model_obj = ClassificationModel.objects.filter(is_active=True).first()
        
        if not model_obj:
            logger.warning("No active classification model found")
            return None
            
        # Load the model and vectorizer
        model_path = os.path.join(settings.MEDIA_ROOT, model_obj.model_file.name)
        vectorizer_path = os.path.join(settings.MEDIA_ROOT, model_obj.vectorizer_file.name)
        
        if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
            logger.error("Model or vectorizer file not found")
            return None
            
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
            
        # Preprocess and vectorize the log message
        log_vector = vectorizer.transform([log_message])
        
        # Get the prediction (class index)
        prediction = model.predict(log_vector)[0]
        
        # Map the prediction to a classification
        classifications = list(LogClassification.objects.all())
        if prediction < len(classifications):
            return classifications[prediction]
        else:
            logger.error(f"Invalid prediction index: {prediction}")
            return None
            
    except Exception as e:
        logger.error(f"Error in ML classification: {str(e)}")
        return None


def train_model():
    """
    Train a new classification model using existing classified logs.
    
    Returns:
        int: ID of the newly created model or None if training fails
    """
    try:
        from logs.models import LogEntry
        from .models import ClassificationModel, LogClassification
        
        # Get all classified logs
        classified_logs = LogEntry.objects.filter(
            classification__isnull=False
        ).select_related('classification')
        
        if classified_logs.count() < 50:
            logger.warning("Not enough classified logs to train a model")
            return None
            
        # Prepare training data
        classifications = list(LogClassification.objects.all())
        if not classifications:
            logger.warning("No classification categories found")
            return None
            
        # Create a mapping from classification to index
        classification_to_index = {
            cls.id: i for i, cls in enumerate(classifications)
        }
            
        # Prepare X (log messages) and y (classification indices)
        log_messages = []
        log_classifications = []
        
        for log in classified_logs:
            log_messages.append(log.message)
            log_classifications.append(
                classification_to_index[log.classification.id]
            )
            
        # Create and train the vectorizer
        vectorizer = TfidfVectorizer(
            max_features=5000, 
            stop_words='english', 
            ngram_range=(1, 2)
        )
        X = vectorizer.fit_transform(log_messages)
        y = np.array(log_classifications)
        
        # Split data into training and testing sets (80/20)
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train the model
        model = MultinomialNB()
        model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save the model and vectorizer
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        model_filename = f'classification_model_{timestamp}.pkl'
        vectorizer_filename = f'classification_vectorizer_{timestamp}.pkl'
        
        model_path = os.path.join(settings.MEDIA_ROOT, 'classification_models', model_filename)
        vectorizer_path = os.path.join(settings.MEDIA_ROOT, 'classification_models', vectorizer_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
            
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
            
        # Create a new model record
        model_obj = ClassificationModel.objects.create(
            name='LogClassifier',
            description='Automatically trained classification model',
            version=timestamp,
            model_file=f'classification_models/{model_filename}',
            vectorizer_file=f'classification_models/{vectorizer_filename}',
            accuracy=accuracy,
            is_active=False,
            trained_at=timezone.now()
        )
        
        logger.info(f"Trained new classification model with accuracy: {accuracy:.4f}")
        return model_obj.id
        
    except Exception as e:
        logger.error(f"Error training classification model: {str(e)}")
        return None 