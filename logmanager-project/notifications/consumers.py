"""
WebSocket consumers for the notifications app.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    """
    
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Get the user from the scope (added by AuthMiddlewareStack)
        self.user = self.scope["user"]
        
        # Reject the connection if the user is not authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Add the user to their personal notification group
        self.group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send any unread notifications
        await self.send_unread_notifications()
    
    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave the group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Called when we receive a text frame from the client.
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'mark_as_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_as_read(notification_id)
            
            elif action == 'get_unread':
                await self.send_unread_notifications()
                
        except json.JSONDecodeError:
            logger.error("Received invalid JSON data")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
    
    async def notification_message(self, event):
        """
        Handler for notification.message event, sends the notification to the client.
        """
        # Send the notification to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        }))
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """
        Mark a notification as read in the database.
        """
        from django.utils import timezone
        from notifications.models import Notification
        
        try:
            # Ensure the notification belongs to this user
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            
            if notification.status != Notification.Status.READ:
                notification.status = Notification.Status.READ
                notification.read_at = timezone.now()
                notification.save(update_fields=['status', 'read_at', 'updated_at'])
            
            return True
        except Notification.DoesNotExist:
            logger.error(f"Notification {notification_id} not found or doesn't belong to user {self.user.id}")
            return False
    
    @database_sync_to_async
    def get_unread_notifications(self):
        """
        Get unread notifications for the current user.
        """
        from notifications.models import Notification
        
        notifications = Notification.objects.filter(
            user=self.user,
            status__in=[Notification.Status.SENT, Notification.Status.DELIVERED]
        ).order_by('-created_at')[:10]
        
        return [
            {
                'id': notification.id,
                'subject': notification.subject,
                'content': notification.content,
                'data': notification.data,
                'created_at': notification.created_at.isoformat(),
            }
            for notification in notifications
        ]
    
    async def send_unread_notifications(self):
        """
        Send unread notifications to the client.
        """
        notifications = await self.get_unread_notifications()
        
        await self.send(text_data=json.dumps({
            'type': 'unread_notifications',
            'notifications': notifications
        })) 