"""
Celery tasks for sending notifications.
"""

import logging
import json
from datetime import datetime
from celery import shared_task
from django.utils import timezone
from django.template import Template, Context
from django.db.models import Q
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


@shared_task
def send_notification(template_name, **kwargs):
    """
    Create and send a notification using the specified template and data.
    
    Args:
        template_name: Name of the notification template to use
        **kwargs: Data for template rendering and recipients selection
    """
    try:
        # Import here to avoid circular imports
        from notifications.models import NotificationTemplate, NotificationChannel, Notification
        
        # Get the template
        template = NotificationTemplate.objects.get(name=template_name)
        
        # Determine recipients based on kwargs
        recipients = []
        User = get_user_model()
        
        # If user_ids are provided directly
        if 'user_ids' in kwargs:
            recipients = User.objects.filter(id__in=kwargs['user_ids'])
        
        # If roles are provided
        elif 'roles' in kwargs:
            recipients = User.objects.filter(role__in=kwargs['roles'])
        
        # If notification is for log classification, notify admins and managers
        elif 'log_entry_id' in kwargs and 'classification_id' in kwargs:
            recipients = User.objects.filter(
                Q(role='ADMIN') | Q(role='MANAGER'),
                notification_email=True
            )
        
        # Default to all active admin users if no specific recipients
        else:
            recipients = User.objects.filter(role='ADMIN', is_active=True)
        
        # Get the available notification channels
        email_channel = NotificationChannel.objects.filter(
            type='EMAIL', is_active=True
        ).first()
        
        websocket_channel = NotificationChannel.objects.filter(
            type='WEBSOCKET', is_active=True
        ).first()
        
        # Prepare the context for template rendering
        context_data = kwargs.copy()
        
        # Add some useful data if we have log entry information
        if 'log_entry_id' in kwargs:
            from logs.models import LogEntry
            try:
                log_entry = LogEntry.objects.get(id=kwargs['log_entry_id'])
                context_data['log_entry'] = {
                    'id': log_entry.id,
                    'message': log_entry.message,
                    'severity': log_entry.severity,
                    'source': log_entry.source.name,
                    'timestamp': log_entry.timestamp.isoformat(),
                }
            except LogEntry.DoesNotExist:
                logger.error(f"Log entry {kwargs['log_entry_id']} not found")
        
        # Add classification information if available
        if 'classification_id' in kwargs:
            from classification.models import LogClassification
            try:
                classification = LogClassification.objects.get(id=kwargs['classification_id'])
                context_data['classification'] = {
                    'id': classification.id,
                    'name': classification.name,
                    'priority': classification.priority,
                }
            except LogClassification.DoesNotExist:
                logger.error(f"Classification {kwargs['classification_id']} not found")
        
        # Create a Django template context
        context = Context(context_data)
        
        # Render the subject and content
        subject = Template(template.subject).render(context)
        content = Template(template.content).render(context)
        html_content = Template(template.html_content).render(context) if template.html_content else None
        
        # Create and send notifications for each recipient
        for user in recipients:
            # Create a notification record for each channel
            if email_channel and user.notification_email:
                notification = Notification.objects.create(
                    user=user,
                    template=template,
                    channel=email_channel,
                    subject=subject,
                    content=content,
                    data=context_data
                )
                # Send via email
                send_email_notification.delay(notification.id)
            
            if websocket_channel:
                notification = Notification.objects.create(
                    user=user,
                    template=template,
                    channel=websocket_channel,
                    subject=subject,
                    content=content,
                    data=context_data
                )
                # Send via websocket
                send_websocket_notification.delay(notification.id)
        
        return f"Created notifications for {len(recipients)} recipients"
    
    except NotificationTemplate.DoesNotExist:
        logger.error(f"Notification template '{template_name}' not found")
        return f"Notification template '{template_name}' not found"
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return f"Error sending notification: {str(e)}"


@shared_task
def send_email_notification(notification_id):
    """
    Send a notification via email.
    """
    try:
        from notifications.models import Notification
        from django.core.mail import send_mail
        
        notification = Notification.objects.get(id=notification_id)
        
        if notification.status != Notification.Status.PENDING:
            return f"Notification {notification_id} is not in PENDING status"
        
        # Get email configuration from the channel
        config = notification.channel.configuration
        from_email = config.get('from_email', 'noreply@example.com')
        
        # Get the recipient's email
        to_email = notification.user.email
        
        # Send the email
        html_message = notification.data.get('html_content', None)
        
        send_mail(
            subject=notification.subject,
            message=notification.content,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Update notification status
        notification.status = Notification.Status.SENT
        notification.sent_at = timezone.now()
        notification.save(update_fields=['status', 'sent_at', 'updated_at'])
        
        return f"Email notification {notification_id} sent to {to_email}"
    
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return f"Notification {notification_id} not found"
    except Exception as e:
        logger.error(f"Error sending email notification {notification_id}: {str(e)}")
        
        # Update notification with error status
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.status = Notification.Status.FAILED
            notification.error_message = str(e)
            notification.save(update_fields=['status', 'error_message', 'updated_at'])
        except:
            pass
        
        return f"Error sending email notification {notification_id}: {str(e)}"


@shared_task
def send_websocket_notification(notification_id):
    """
    Send a notification via WebSocket.
    """
    try:
        from notifications.models import Notification
        
        notification = Notification.objects.get(id=notification_id)
        
        if notification.status != Notification.Status.PENDING:
            return f"Notification {notification_id} is not in PENDING status"
        
        # Get the channel layer
        channel_layer = get_channel_layer()
        
        # Prepare the message
        message = {
            'id': notification.id,
            'subject': notification.subject,
            'content': notification.content,
            'data': notification.data,
            'created_at': notification.created_at.isoformat(),
        }
        
        # Send to the user's channel group
        async_to_sync(channel_layer.group_send)(
            f"user_{notification.user.id}",
            {
                'type': 'notification.message',
                'message': message
            }
        )
        
        # Update notification status
        notification.status = Notification.Status.SENT
        notification.sent_at = timezone.now()
        notification.save(update_fields=['status', 'sent_at', 'updated_at'])
        
        return f"WebSocket notification {notification_id} sent to user {notification.user.id}"
    
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return f"Notification {notification_id} not found"
    except Exception as e:
        logger.error(f"Error sending WebSocket notification {notification_id}: {str(e)}")
        
        # Update notification with error status
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.status = Notification.Status.FAILED
            notification.error_message = str(e)
            notification.save(update_fields=['status', 'error_message', 'updated_at'])
        except:
            pass
        
        return f"Error sending WebSocket notification {notification_id}: {str(e)}" 