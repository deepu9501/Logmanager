"""
Serializers for the users app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserActivity

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user objects with full details.
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'role_display', 'department', 'phone',
            'notification_email', 'notification_sms',
            'is_active', 'date_joined', 'last_login',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile that allows users to update their own information.
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'role_display', 'department', 'phone',
            'notification_email', 'notification_sms',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'role', 'role_display', 
            'created_at', 'updated_at'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new user accounts.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'department', 
            'phone', 'notification_email', 'notification_sms'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activity logs.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'username', 'ip_address',
            'action', 'object_type', 'object_id',
            'details', 'created_at'
        ]
        read_only_fields = fields 